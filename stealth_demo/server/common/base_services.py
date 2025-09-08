"""
Abstract base class for cryptographic scheme services.
Provides common logic for key generation, address operations, and tracing,
delegating scheme-specific C library calls to concrete implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from ..multi_scheme_config import config # Corrected import
from .base_utils import hex_to_bytes_safe, validate_index
from .scheme_utils import get_element_size, create_buffer, create_multiple_buffers, bytes_to_hex_safe_fixed, find_matching_key
from ctypes import c_double # For performance test results array


class BaseSchemeService(ABC):
    """
    Abstract base class for cryptographic scheme services.
    Defines the common interface and implements shared logic.
    """

    def __init__(self):
        # Ensure the scheme name is set in the concrete class
        if not hasattr(self, '_scheme_name'):
            raise NotImplementedError("Concrete service class must define _scheme_name")

    @abstractmethod
    def _get_lib(self):
        """Returns the scheme-specific C library wrapper instance."""
        pass

    @abstractmethod
    def _generate_tracer_key_with_param(self, param_file: str) -> Dict:
        """
        Generates the scheme-specific tracer key pair.
        This method is abstract because the C function call and key names might differ.
        """
        pass

    @abstractmethod
    def _call_c_keygen(self, A_buf, B_buf, a_buf, b_buf, buf_size: int):
        """Calls the scheme-specific C key generation function."""
        pass

    @abstractmethod
    def _call_c_addr_gen(self, *args):
        """Calls the scheme-specific C address generation function."""
        pass

    @abstractmethod
    def _call_c_recognize_address(self, address_data: Dict, key_data: Dict, fast: bool = True) -> bool:
        """Calls the scheme-specific C address recognition function."""
        pass

    @abstractmethod
    def _call_c_generate_dsk(self, address_data: Dict, key_data: Dict) -> Dict:
        """Calls the scheme-specific C DSK generation function."""
        pass

    @abstractmethod
    def _call_c_trace_identity(self, address_data: Dict) -> Dict:
        """Calls the scheme-specific C identity tracing function."""
        pass

    @abstractmethod
    def _call_c_performance_test(self, iterations: int) -> Dict:
        """Calls the scheme-specific C performance test function."""
        pass

    # Common implementations for service methods

    def setup_system(self, param_file: str) -> Dict:
        """Initialize the cryptographic system for the current scheme."""
        config.set_current_scheme(self._scheme_name)
        full_path = config.validate_param_file(param_file)

        print(f"🔧 Initializing {self._scheme_name} with {full_path}")
        lib = self._get_lib()
        result = lib.init(full_path)

        if result != 0:
            raise Exception(f"{self._scheme_name} library initialization failed with code: {result}")

        if not lib.is_initialized():
            raise Exception(f"{self._scheme_name} library initialization verification failed")

        config.reset_scheme(self._scheme_name)

        tracer_key = self._generate_tracer_key_with_param(param_file)
        config.set_initialized(param_file, tracer_key, self._scheme_name)

        g1_size, zr_size = lib.get_element_sizes()

        response = {
            "status": "setup complete",
            "message": f"{self._scheme_name} system initialized with {param_file}",
            "param_file": param_file,
            "g1_size": g1_size,
            "zr_size": zr_size,
            "scheme": self._scheme_name,
            **tracer_key
        }
        
        # Add DSK functions availability if the library has it
        if hasattr(lib, 'dsk_functions_available'):
            config.get_scheme_data(self._scheme_name)['dsk_functions_available'] = lib.dsk_functions_available
            response['dsk_functions_available'] = lib.dsk_functions_available

        return response

    def generate_keypair(self) -> Dict:
        """Generate a new key pair for the current scheme."""
        config.set_current_scheme(self._scheme_name)
        config.ensure_initialized(self._scheme_name)

        buf_size = get_element_size()
        A_buf, B_buf, a_buf, b_buf = create_multiple_buffers(4, buf_size)

        self._call_c_keygen(A_buf, B_buf, a_buf, b_buf, buf_size)

        A_hex = bytes_to_hex_safe_fixed(A_buf, 'G1')
        B_hex = bytes_to_hex_safe_fixed(B_buf, 'G1')
        a_hex = bytes_to_hex_safe_fixed(a_buf, 'Zr')
        b_hex = bytes_to_hex_safe_fixed(b_buf, 'Zr')

        if not all([A_hex, B_hex, a_hex, b_hex]):
            raise Exception(f"Failed to generate {self._scheme_name} key pair")

        item = {
            "index": len(config.key_list),
            "id": f"key_{len(config.key_list)}",
            "A_hex": A_hex,
            "B_hex": B_hex,
            "a_hex": a_hex,
            "b_hex": b_hex,
            "param_file": config.current_param_file,
            "scheme": self._scheme_name,
            "status": "generated"
        }

        config.key_list.append(item)
        return item

    def generate_address(self, key_index: int) -> Dict:
        """Generate address with selected key for the current scheme."""
        config.set_current_scheme(self._scheme_name)
        config.ensure_initialized(self._scheme_name)
        validate_index(key_index, config.key_list, "key_index")

        if config.trace_key is None:
            raise Exception("Tracer key not initialized")

        selected_key = config.key_list[key_index]

        # Scheme-specific arguments for C call
        A_r_hex = selected_key['A_hex']
        B_r_hex = selected_key['B_hex']
        A_m_hex = config.trace_key['TK_hex']  # Tracer public key

        A_r_bytes = hex_to_bytes_safe(A_r_hex)
        B_r_bytes = hex_to_bytes_safe(B_r_hex)
        A_m_bytes = hex_to_bytes_safe(A_m_hex)

        buf_size = get_element_size()
        addr_buf, r1_buf, r2_buf = create_multiple_buffers(3, buf_size)
        
        # Call scheme-specific C function
        self._call_c_addr_gen(A_r_bytes, B_r_bytes, A_m_bytes, addr_buf, r1_buf, r2_buf, buf_size)

        addr_hex = bytes_to_hex_safe_fixed(addr_buf, 'G1')
        r1_hex = bytes_to_hex_safe_fixed(r1_buf, 'G1')
        r2_hex = bytes_to_hex_safe_fixed(r2_buf, 'G1')

        if not all([addr_hex, r1_hex, r2_hex]):
            raise Exception(f"Failed to generate {self._scheme_name} address")

        address_item = {
            "index": len(config.address_list),
            "id": f"addr_{len(config.address_list)}",
            "addr_hex": addr_hex,
            "r1_hex": r1_hex,
            "r2_hex": r2_hex,
            "key_index": key_index,
            "key_id": selected_key['id'],
            "owner_A": A_r_hex,
            "owner_B": B_r_hex,
            "scheme": self._scheme_name,
            "status": "generated"
        }

        config.address_list.append(address_item) # Corrected from 'item'
        return address_item # Corrected from 'item'

    def recognize_address(self, address_index: int, key_index: int, fast: bool = True) -> Dict:
        """Recognize address with selected key for the current scheme."""
        config.set_current_scheme(self._scheme_name)
        config.ensure_initialized(self._scheme_name)
        validate_index(address_index, config.address_list, "address_index")
        validate_index(key_index, config.key_list, "key_index")
        
        address_data = config.address_list[address_index]
        key_data = config.key_list[key_index]

        recognized = self._call_c_recognize_address(address_data, key_data, fast)
        method = "fast" if fast else "full"

        return {
            "recognized": recognized,
            "address_index": address_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "is_owner": (address_data['key_index'] == key_index),
            "method": method,
            "scheme": self._scheme_name,
            "status": "recognized" if recognized else "not_recognized"
        }

    def generate_dsk(self, address_index: int, key_index: int) -> Dict:
        """Generate one-time secret key for selected address and key."""
        config.set_current_scheme(self._scheme_name)
        config.ensure_initialized(self._scheme_name)
        validate_index(address_index, config.address_list, "address_index")
        validate_index(key_index, config.key_list, "key_index")
        
        address_data = config.address_list[address_index]
        key_data = config.key_list[key_index]

        dsk_item = self._call_c_generate_dsk(address_data, key_data)
        
        config.dsk_list.append(dsk_item)
        return dsk_item

    def trace_identity(self, address_index: int) -> Dict:
        """Trace identity for selected address."""
        config.set_current_scheme(self._scheme_name)
        config.ensure_initialized(self._scheme_name)
        validate_index(address_index, config.address_list, "address_index")

        if config.trace_key is None:
            raise Exception("Tracer key not initialized")
        
        address_data = config.address_list[address_index]

        trace_result = self._call_c_trace_identity(address_data)
        
        return {
            "recovered_b_hex": trace_result["recovered_b_hex"],
            "address_index": address_index,
            "address_id": address_data['id'],
            "original_owner": {
                "key_index": address_data['key_index'],
                "key_id": address_data['key_id'],
                "B_hex": address_data['owner_B']
            },
            "matched_key": trace_result["matched_key"],
            "perfect_match": trace_result["perfect_match"],
            "scheme": self._scheme_name,
            "status": "traced"
        }

    def performance_test(self, iterations: int = 100) -> Dict:
        """Run performance test for the current scheme."""
        config.set_current_scheme(self._scheme_name)
        config.ensure_initialized(self._scheme_name)
        
        iterations = min(iterations, 1000) # Limit iterations to prevent excessive load

        results_dict = self._call_c_performance_test(iterations)

        return {
            "iterations": iterations,
            "scheme": self._scheme_name,
            "status": "completed",
            **results_dict
        }

    # Placeholder for signing/verification methods, to be overridden by schemes that support them
    def sign_message(self, *args, **kwargs) -> Dict:
        raise NotImplementedError(f"Message signing not supported by {self._scheme_name} scheme.")

    def verify_signature(self, *args, **kwargs) -> Dict:
        raise NotImplementedError(f"Signature verification not supported by {self._scheme_name} scheme.")

    def sign_with_address_and_dsk(self, *args, **kwargs) -> Dict:
        raise NotImplementedError(f"Signing with address and DSK not supported by {self._scheme_name} scheme.")
