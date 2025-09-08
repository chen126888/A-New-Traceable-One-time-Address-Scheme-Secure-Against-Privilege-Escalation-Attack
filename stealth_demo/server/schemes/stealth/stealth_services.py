"""
Cryptographic services module for stealth operations.
Hangles key generation, address operations, signing, verification, and tracing.
"""
from typing import Dict, Optional
from .stealth_wrapper import get_stealth_lib
from ...multi_scheme_config import config
from ...common.base_utils import hex_to_bytes_safe, validate_index
from ...common.scheme_utils import get_element_size, create_buffer, create_multiple_buffers, bytes_to_hex_safe_fixed, find_matching_key
from ...common.base_services import BaseSchemeService # Import the base class
from ctypes import c_double # For performance test results array


# Initialize stealth lib when needed
def _get_lib():
    return get_stealth_lib()


class StealthServices(BaseSchemeService):
    """High-level cryptographic operations."""

    def __init__(self):
        self._scheme_name = 'stealth' # Set it before calling super().__init__()
        super().__init__()

    def _get_lib(self):
        return _get_lib()

    def _generate_tracer_key_with_param(self, param_file: str) -> Dict:
        stealth_lib = self._get_lib()
        g1_size, zr_size = stealth_lib.get_element_sizes()
        buf_size = max(g1_size, zr_size, 512)
        TK_buf, k_buf = create_multiple_buffers(2, buf_size)

        stealth_lib.tracekeygen(TK_buf, k_buf, buf_size)

        tk_hex = bytes_to_hex_safe_fixed(TK_buf, 'G1')
        k_hex = bytes_to_hex_safe_fixed(k_buf, 'Zr')

        if not tk_hex or not k_hex:
            raise Exception("Failed to generate trace key")

        return {
            "TK_hex": tk_hex,
            "k_hex": k_hex,
            "param_file": param_file,
            "status": "initialized"
        }

    def _call_c_keygen(self, A_buf, B_buf, a_buf, b_buf, buf_size: int):
        stealth_lib = self._get_lib()
        stealth_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)

    def _call_c_addr_gen(self, A_bytes, B_bytes, TK_bytes, addr_buf, r1_buf, r2_buf, c_buf, buf_size: int):
        stealth_lib = self._get_lib()
        stealth_lib.addr_gen(A_bytes, B_bytes, TK_bytes,
                           addr_buf, r1_buf, r2_buf, c_buf, buf_size)

    def generate_address(self, key_index: int) -> Dict:
        """Generate stealth address with selected key."""
        config.set_current_scheme(self._scheme_name)
        config.ensure_initialized(self._scheme_name)
        validate_index(key_index, config.key_list, "key_index")

        if config.trace_key is None:
            raise Exception("Trace key not initialized")

        selected_key = config.key_list[key_index]

        A_hex = selected_key['A_hex']
        B_hex = selected_key['B_hex']
        TK_hex = config.trace_key['TK_hex']

        A_bytes = hex_to_bytes_safe(A_hex)
        B_bytes = hex_to_bytes_safe(B_hex)
        TK_bytes = hex_to_bytes_safe(TK_hex)

        buf_size = get_element_size()
        addr_buf, r1_buf, r2_buf, c_buf = create_multiple_buffers(4, buf_size)

        stealth_lib = self._get_lib()
        stealth_lib.addr_gen(A_bytes, B_bytes, TK_bytes,
                           addr_buf, r1_buf, r2_buf, c_buf, buf_size)

        addr_hex = bytes_to_hex_safe_fixed(addr_buf, 'G1')
        r1_hex = bytes_to_hex_safe_fixed(r1_buf, 'G1')
        r2_hex = bytes_to_hex_safe_fixed(r2_buf, 'G1')
        c_hex = bytes_to_hex_safe_fixed(c_buf, 'G1') # Specific to Stealth

        if not all([addr_hex, r1_hex, r2_hex, c_hex]):
            raise Exception(f"Failed to generate {self._scheme_name} address")

        address_item = {
            "index": len(config.address_list),
            "id": f"addr_{len(config.address_list)}",
            "addr_hex": addr_hex,
            "r1_hex": r1_hex,
            "r2_hex": r2_hex,
            "c_hex": c_hex, # Specific to Stealth
            "key_index": key_index,
            "key_id": selected_key['id'],
            "owner_A": A_hex,
            "owner_B": B_hex,
            "scheme": self._scheme_name,
            "status": "generated"
        }

        config.address_list.append(address_item)
        return address_item

    def _call_c_recognize_address(self, address_data: Dict, key_data: Dict, fast: bool = True) -> bool:
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        b_bytes = hex_to_bytes_safe(key_data['B_hex'])
        a_bytes = hex_to_bytes_safe(key_data['A_hex'])
        c_bytes = hex_to_bytes_safe(address_data['c_hex'])
        a_priv_bytes = hex_to_bytes_safe(key_data['a_hex'])

        stealth_lib = self._get_lib()
        # Stealth only has one recognition method (fast) exposed via this API
        result = stealth_lib.addr_recognize_fast(r1_bytes, b_bytes, a_bytes, c_bytes, a_priv_bytes)
        return result

    def _call_c_generate_dsk(self, address_data: Dict, key_data: Dict) -> Dict:
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        a_bytes = hex_to_bytes_safe(key_data['a_hex'])
        b_bytes = hex_to_bytes_safe(key_data['b_hex'])

        buf_size = get_element_size()
        dsk_buf = create_buffer(buf_size)

        stealth_lib = self._get_lib()
        if config.get_scheme_data(self._scheme_name)['dsk_functions_available']:
            stealth_lib.dsk_gen(addr_bytes, r1_bytes, a_bytes, b_bytes, dsk_buf, buf_size)
            method = "dedicated"
        else:
            # Fallback: use the original sign function and extract DSK
            temp_q_buf, temp_h_buf = create_multiple_buffers(2, buf_size)
            stealth_lib.sign(addr_bytes, r1_bytes, a_bytes, b_bytes, b"temp_message",
                           temp_q_buf, temp_h_buf, dsk_buf, buf_size)
            method = "fallback"

        dsk_hex = bytes_to_hex_safe_fixed(dsk_buf, 'G1')

        if not dsk_hex:
            raise Exception("Failed to generate DSK")

        return {
            "index": len(config.dsk_list),
            "id": f"dsk_{len(config.dsk_list)}",
            "dsk_hex": dsk_hex,
            "address_index": address_data['index'],
            "key_index": key_data['index'],
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "owner_A": key_data['A_hex'],
            "owner_B": key_data['B_hex'],
            "for_address": address_data['addr_hex'],
            "method": method,
            "scheme": self._scheme_name,
            "status": "generated"
        }

    def _call_c_trace_identity(self, address_data: Dict) -> Dict:
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        r2_bytes = hex_to_bytes_safe(address_data['r2_hex'])
        c_bytes = hex_to_bytes_safe(address_data['c_hex'])
        k_bytes = hex_to_bytes_safe(config.trace_key['k_hex'])

        buf_size = get_element_size()
        b_recovered_buf = create_buffer(buf_size)

        stealth_lib = self._get_lib()
        stealth_lib.trace(addr_bytes, r1_bytes, r2_bytes, c_bytes, k_bytes,
                        b_recovered_buf, buf_size)

        b_recovered_hex = bytes_to_hex_safe_fixed(b_recovered_buf, 'G1')

        if not b_recovered_hex:
            raise Exception("Failed to trace identity")

        matched_key = find_matching_key(b_recovered_hex)

        return {
            "recovered_b_hex": b_recovered_hex,
            "matched_key": matched_key,
            "perfect_match": matched_key is not None,
        }

    def _call_c_performance_test(self, iterations: int) -> Dict:
        results = (c_double * 7)()
        stealth_lib = self._get_lib()
        stealth_lib.performance_test(iterations, results)
        return {
            "addr_gen_ms": round(results[0], 3),
            "addr_recognize_ms": round(results[1], 3),
            "fast_recognize_ms": round(results[2], 3),
            "onetime_sk_ms": round(results[3], 3),
            "sign_ms": round(results[4], 3),
            "sig_verify_ms": round(results[5], 3),
            "trace_ms": round(results[6], 3),
        }

    # Override signing/verification methods as Stealth supports them
    def sign_message(self, message: str, dsk_index: Optional[int] = None,
                    address_index: Optional[int] = None, key_index: Optional[int] = None) -> Dict:
        """Sign message with DSK or key pair."""
        config.ensure_initialized()
        message_bytes = message.encode('utf-8')

        if dsk_index is not None:
            return self._sign_with_dsk(message, message_bytes, dsk_index)
        elif address_index is not None and key_index is not None:
            return self._sign_with_keypair(message, message_bytes, address_index, key_index)
        else:
            raise ValueError("Must specify either dsk_index or (address_index and key_index)")

    def _sign_with_dsk(self, message: str, message_bytes: bytes, dsk_index: int) -> Dict:
        """Sign message with DSK."""
        validate_index(dsk_index, config.dsk_list, "dsk_index")

        if not config.get_scheme_data(self._scheme_name)['dsk_functions_available']:
            raise Exception("DSK signing not available in fallback mode")

        dsk_data = config.dsk_list[dsk_index]
        address_data = config.address_list[dsk_data['address_index']]

        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        dsk_bytes = hex_to_bytes_safe(dsk_data['dsk_hex'])

        buf_size = get_element_size()
        q_sigma_buf, h_buf = create_multiple_buffers(2, buf_size)

        stealth_lib = self._get_lib()
        stealth_lib.sign_with_dsk(addr_bytes, dsk_bytes, message_bytes,
                                q_sigma_buf, h_buf, buf_size)

        q_sigma_hex = bytes_to_hex_safe_fixed(q_sigma_buf, 'G1')
        h_hex = bytes_to_hex_safe_fixed(h_buf, 'Zr')

        if not q_sigma_hex or not h_hex:
            raise Exception("Failed to sign message with DSK")

        return {
            "message": message,
            "q_sigma_hex": q_sigma_hex,
            "h_hex": h_hex,
            "dsk_index": dsk_index,
            "dsk_id": dsk_data['id'],
            "address_index": dsk_data['address_index'],
            "address_id": address_data['id'],
            "method": "dsk",
            "status": "signed"
        }

    def _sign_with_keypair(self, message: str, message_bytes: bytes, address_index: int, key_index: int) -> Dict:
        """Sign message with key pair."""
        validate_index(address_index, config.address_list, "address_index")
        validate_index(key_index, config.key_list, "key_index")

        address_data = config.address_list[address_index]
        key_data = config.key_list[key_index]

        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        a_bytes = hex_to_bytes_safe(key_data['a_hex'])
        b_bytes = hex_to_bytes_safe(key_data['b_hex'])

        buf_size = get_element_size()
        q_sigma_buf, h_buf, dsk_buf = create_multiple_buffers(3, buf_size)

        stealth_lib = self._get_lib()
        stealth_lib.sign(addr_bytes, r1_bytes, a_bytes, b_bytes, message_bytes,
                           q_sigma_buf, h_buf, dsk_buf, buf_size)

        q_sigma_hex = bytes_to_hex_safe_fixed(q_sigma_buf, 'G1')
        h_hex = bytes_to_hex_safe_fixed(h_buf, 'Zr')
        dsk_hex = bytes_to_hex_safe_fixed(dsk_buf, 'G1')

        if not q_sigma_hex or not h_hex:
            raise Exception("Failed to sign message with key")

        return {
            "message": message,
            "q_sigma_hex": q_sigma_hex,
            "h_hex": h_hex,
            "dsk_hex": dsk_hex,
            "address_index": address_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "method": "keypair",
            "status": "signed"
        }

    def sign_with_address_and_dsk(self, message: str, address_index: int, dsk_index: int) -> Dict:
        """Sign message using specific address and DSK - allows testing of correct/incorrect matches."""
        config.ensure_initialized()
        validate_index(address_index, config.address_list, "address_index")
        validate_index(dsk_index, config.dsk_list, "dsk_index")

        if not config.get_scheme_data(self._scheme_name)['dsk_functions_available']:
            raise Exception("DSK signing not available in fallback mode")

        address_data = config.address_list[address_index]
        dsk_data = config.dsk_list[dsk_index]

        message_bytes = message.encode('utf-8')
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        dsk_bytes = hex_to_bytes_safe(dsk_data['dsk_hex'])

        buf_size = get_element_size()
        q_sigma_buf, h_buf = create_multiple_buffers(2, buf_size)

        stealth_lib = self._get_lib()
        stealth_lib.sign_with_dsk(addr_bytes, dsk_bytes, message_bytes,
                                q_sigma_buf, h_buf, buf_size)

        q_sigma_hex = bytes_to_hex_safe_fixed(q_sigma_buf, 'G1')
        h_hex = bytes_to_hex_safe_fixed(h_buf, 'Zr')

        if not q_sigma_hex or not h_hex:
            raise Exception("Failed to sign message with address and DSK")

        # Check if this is a correct match (DSK was generated for this address)
        is_correct_match = dsk_data['address_index'] == address_index

        return {
            "message": message,
            "q_sigma_hex": q_sigma_hex,
            "h_hex": h_hex,
            "address_index": address_index,
            "address_id": address_data['id'],
            "dsk_index": dsk_index,
            "dsk_id": dsk_data['id'],
            "dsk_for_address": dsk_data['address_id'],
            "is_correct_match": is_correct_match,
            "match_status": "correct" if is_correct_match else "incorrect",
            "method": "address_dsk",
            "status": "signed"
        }

    def verify_signature(self, message: str, q_sigma_hex: str, h_hex: str, address_index: int) -> Dict:
        """Verify signature."""
        config.ensure_initialized()
        validate_index(address_index, config.address_list, "address_index")

        address_data = config.address_list[address_index]

        message_bytes = message.encode('utf-8')
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r2_bytes = hex_to_bytes_safe(address_data['r2_hex'])
        c_bytes = hex_to_bytes_safe(address_data['c_hex'])
        h_bytes = hex_to_bytes_safe(h_hex)
        q_sigma_bytes = hex_to_bytes_safe(q_sigma_hex)

        stealth_lib = self._get_lib()
        result = stealth_lib.verify(addr_bytes, r2_bytes, c_bytes, message_bytes, h_bytes, q_sigma_bytes)

        return {
            "valid": result,
            "message": message,
            "address_index": address_index,
            "address_id": address_data['id'],
            "status": "verified" if result else "invalid"
        }
