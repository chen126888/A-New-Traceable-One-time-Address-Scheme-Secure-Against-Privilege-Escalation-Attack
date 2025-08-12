"""
Cryptographic services module for SITAIBA operations.
Handles key generation, address operations, DSK generation, recognition, and tracing.
Note: SITAIBA scheme does not support message signing/verification.
"""
from typing import Dict, Optional
from .sitaiba_wrapper import get_sitaiba_lib
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from multi_scheme_config import config
from .sitaiba_utils import (
    get_element_size, create_buffer, create_multiple_buffers,
    bytes_to_hex_safe_fixed, hex_to_bytes_safe, validate_index, find_matching_key
)

# Initialize SITAIBA lib when needed
def _get_lib():
    return get_sitaiba_lib()


class SitaibaServices:
    """High-level SITAIBA cryptographic operations."""
    
    @staticmethod
    def setup_system(param_file: str) -> Dict:
        """Initialize the SITAIBA cryptographic system."""
        # Set current scheme to SITAIBA
        config.set_current_scheme('sitaiba')
        
        full_path = config.validate_param_file(param_file)
        
        print(f"🔧 Initializing SITAIBA with {full_path}")
        sitaiba_lib = _get_lib()
        result = sitaiba_lib.init(full_path)
        
        if result != 0:
            raise Exception(f"SITAIBA library initialization failed with code: {result}")
        
        if not sitaiba_lib.is_initialized():
            raise Exception("SITAIBA library initialization verification failed")
        
        # Clear existing data for SITAIBA scheme
        config.reset_scheme('sitaiba')
        
        # Generate tracer key (pass param_file since config is reset)
        tracer_key = SitaibaServices._generate_tracer_key_with_param(param_file)
        config.set_initialized(param_file, tracer_key, 'sitaiba')
        
        g1_size, zr_size = sitaiba_lib.get_element_sizes()
        
        return {
            "status": "setup complete",
            "message": f"SITAIBA system initialized with {param_file}",
            "param_file": param_file,
            "g1_size": g1_size,
            "zr_size": zr_size,
            "scheme": "sitaiba",
            **tracer_key
        }
    
    @staticmethod
    def _generate_tracer_key_with_param(param_file: str) -> Dict:
        """Generate tracer key pair with specific param file."""
        sitaiba_lib = _get_lib()
        g1_size, zr_size = sitaiba_lib.get_element_sizes()
        buf_size = max(g1_size, zr_size, 512)
        A_m_buf, a_m_buf = create_multiple_buffers(2, buf_size)
        
        sitaiba_lib.tracer_keygen(A_m_buf, a_m_buf, buf_size)
        
        A_m_hex = bytes_to_hex_safe_fixed(A_m_buf, 'G1')
        a_m_hex = bytes_to_hex_safe_fixed(a_m_buf, 'Zr')
        
        if not A_m_hex or not a_m_hex:
            raise Exception("Failed to generate SITAIBA tracer key")
        
        return {
            "TK_hex": A_m_hex,  # Using same key name for consistency
            "k_hex": a_m_hex,   # Using same key name for consistency
            "param_file": param_file,
            "status": "initialized"
        }
    
    @staticmethod
    def generate_keypair() -> Dict:
        """Generate a new SITAIBA key pair (A, B, a, b)."""
        config.set_current_scheme('sitaiba')
        config.ensure_initialized('sitaiba')
        
        buf_size = get_element_size()
        A_buf, B_buf, a_buf, b_buf = create_multiple_buffers(4, buf_size)
        
        sitaiba_lib = _get_lib()
        sitaiba_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
        
        A_hex = bytes_to_hex_safe_fixed(A_buf, 'G1')
        B_hex = bytes_to_hex_safe_fixed(B_buf, 'G1')
        a_hex = bytes_to_hex_safe_fixed(a_buf, 'Zr')
        b_hex = bytes_to_hex_safe_fixed(b_buf, 'Zr')
        
        if not all([A_hex, B_hex, a_hex, b_hex]):
            raise Exception("Failed to generate SITAIBA key pair")
        
        item = {
            "index": len(config.key_list),
            "id": f"key_{len(config.key_list)}",
            "A_hex": A_hex,
            "B_hex": B_hex,
            "a_hex": a_hex,
            "b_hex": b_hex,
            "param_file": config.current_param_file,
            "scheme": "sitaiba",
            "status": "generated"
        }
        
        config.key_list.append(item)
        return item
    
    @staticmethod
    def generate_address(key_index: int) -> Dict:
        """Generate SITAIBA address with selected key."""
        config.set_current_scheme('sitaiba')
        config.ensure_initialized('sitaiba')
        validate_index(key_index, config.key_list, "key_index")
        
        if config.trace_key is None:
            raise Exception("Tracer key not initialized")
        
        selected_key = config.key_list[key_index]
        
        A_r_hex = selected_key['A_hex']
        B_r_hex = selected_key['B_hex']
        A_m_hex = config.trace_key['TK_hex']  # Tracer public key
        
        A_r_bytes = hex_to_bytes_safe(A_r_hex)
        B_r_bytes = hex_to_bytes_safe(B_r_hex)
        A_m_bytes = hex_to_bytes_safe(A_m_hex)
        
        buf_size = get_element_size()
        addr_buf, r1_buf, r2_buf = create_multiple_buffers(3, buf_size)
        
        sitaiba_lib = _get_lib()
        sitaiba_lib.addr_gen(A_r_bytes, B_r_bytes, A_m_bytes, addr_buf, r1_buf, r2_buf, buf_size)
        
        addr_hex = bytes_to_hex_safe_fixed(addr_buf, 'G1')
        r1_hex = bytes_to_hex_safe_fixed(r1_buf, 'G1')
        r2_hex = bytes_to_hex_safe_fixed(r2_buf, 'G1')
        
        if not all([addr_hex, r1_hex, r2_hex]):
            raise Exception("Failed to generate SITAIBA address")
        
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
            "scheme": "sitaiba",
            "status": "generated"
        }
        
        config.address_list.append(address_item)
        return address_item
    
    @staticmethod
    def recognize_address(address_index: int, key_index: int, fast: bool = True) -> Dict:
        """Recognize SITAIBA address with selected key."""
        config.set_current_scheme('sitaiba')
        config.ensure_initialized('sitaiba')
        validate_index(address_index, config.address_list, "address_index")
        validate_index(key_index, config.key_list, "key_index")
        
        address_data = config.address_list[address_index]
        key_data = config.key_list[key_index]
        
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        r2_bytes = hex_to_bytes_safe(address_data['r2_hex'])
        A_r_bytes = hex_to_bytes_safe(key_data['A_hex'])
        a_r_bytes = hex_to_bytes_safe(key_data['a_hex'])
        
        sitaiba_lib = _get_lib()
        
        if fast:
            # Fast recognition only needs r1, r2, A, a
            result = sitaiba_lib.addr_recognize_fast(r1_bytes, r2_bytes, A_r_bytes, a_r_bytes)
            method = "fast"
        else:
            # Full recognition needs all parameters
            addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
            B_r_bytes = hex_to_bytes_safe(key_data['B_hex'])
            A_m_hex = config.trace_key['TK_hex']
            A_m_bytes = hex_to_bytes_safe(A_m_hex)
            
            result = sitaiba_lib.addr_recognize(addr_bytes, r1_bytes, r2_bytes, 
                                              A_r_bytes, B_r_bytes, a_r_bytes, A_m_bytes)
            method = "full"
        
        return {
            "recognized": result,
            "address_index": address_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "is_owner": (address_data['key_index'] == key_index),
            "method": method,
            "scheme": "sitaiba",
            "status": "recognized" if result else "not_recognized"
        }
    
    @staticmethod
    def generate_dsk(address_index: int, key_index: int) -> Dict:
        """Generate one-time secret key for selected address and key."""
        config.set_current_scheme('sitaiba')
        config.ensure_initialized('sitaiba')
        validate_index(address_index, config.address_list, "address_index")
        validate_index(key_index, config.key_list, "key_index")
        
        address_data = config.address_list[address_index]
        key_data = config.key_list[key_index]
        
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        a_r_bytes = hex_to_bytes_safe(key_data['a_hex'])
        b_r_bytes = hex_to_bytes_safe(key_data['b_hex'])
        
        # Use tracer public key (can pass None to use internal key)
        A_m_hex = config.trace_key['TK_hex']
        A_m_bytes = hex_to_bytes_safe(A_m_hex)
        
        buf_size = get_element_size()
        dsk_buf = create_buffer(buf_size)
        
        sitaiba_lib = _get_lib()
        sitaiba_lib.onetime_skgen(r1_bytes, a_r_bytes, b_r_bytes, A_m_bytes, dsk_buf, buf_size)
        
        dsk_hex = bytes_to_hex_safe_fixed(dsk_buf, 'Zr')  # DSK is in Zr group for SITAIBA
        
        if not dsk_hex:
            raise Exception("Failed to generate SITAIBA DSK")
        
        dsk_item = {
            "index": len(config.dsk_list),
            "id": f"dsk_{len(config.dsk_list)}",
            "dsk_hex": dsk_hex,
            "address_index": address_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "owner_A": key_data['A_hex'],
            "owner_B": key_data['B_hex'],
            "for_address": address_data['addr_hex'],
            "scheme": "sitaiba",
            "status": "generated"
        }
        
        config.dsk_list.append(dsk_item)
        return dsk_item
    
    @staticmethod
    def trace_identity(address_index: int) -> Dict:
        """Trace identity for selected SITAIBA address."""
        config.set_current_scheme('sitaiba')
        config.ensure_initialized('sitaiba')
        validate_index(address_index, config.address_list, "address_index")
        
        if config.trace_key is None:
            raise Exception("Tracer key not initialized")
        
        address_data = config.address_list[address_index]
        
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        r2_bytes = hex_to_bytes_safe(address_data['r2_hex'])
        
        # Use tracer private key a_m
        a_m_hex = config.trace_key['k_hex']  # tracer private key
        a_m_bytes = hex_to_bytes_safe(a_m_hex)
        
        buf_size = get_element_size()
        B_r_buf = create_buffer(buf_size)
        
        sitaiba_lib = _get_lib()
        sitaiba_lib.trace(addr_bytes, r1_bytes, r2_bytes, a_m_bytes, B_r_buf, buf_size)
        
        B_recovered_hex = bytes_to_hex_safe_fixed(B_r_buf, 'G1')
        
        if not B_recovered_hex:
            raise Exception("Failed to trace SITAIBA identity")
        
        # Find matching key
        matched_key = find_matching_key(B_recovered_hex)
        
        return {
            "recovered_b_hex": B_recovered_hex,
            "address_index": address_index,
            "address_id": address_data['id'],
            "original_owner": {
                "key_index": address_data['key_index'],
                "key_id": address_data['key_id'],
                "B_hex": address_data['owner_B']
            },
            "matched_key": matched_key,
            "perfect_match": matched_key is not None,
            "scheme": "sitaiba",
            "status": "traced"
        }
    
    @staticmethod
    def performance_test(iterations: int = 100) -> Dict:
        """Run SITAIBA performance test."""
        config.set_current_scheme('sitaiba')
        config.ensure_initialized('sitaiba')
        
        # Limit iterations to prevent excessive load
        iterations = min(iterations, 1000)
        
        # Create results array - SITAIBA has 5 functions
        from ctypes import c_double
        results = (c_double * 5)()
        
        sitaiba_lib = _get_lib()
        sitaiba_lib.performance_test(iterations, results)
        
        return {
            "iterations": iterations,
            "addr_gen_ms": round(results[0], 3),
            "addr_recognize_ms": round(results[1], 3),
            "fast_recognize_ms": round(results[2], 3),
            "onetime_sk_ms": round(results[3], 3),
            "trace_ms": round(results[4], 3),
            "scheme": "sitaiba",
            "status": "completed"
        }