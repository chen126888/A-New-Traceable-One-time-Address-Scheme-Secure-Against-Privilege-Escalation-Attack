"""
Cryptographic services module for stealth operations.
Handles key generation, address operations, signing, verification, and tracing.
"""
from typing import Dict, Optional
from library_wrapper import stealth_lib
from config import config
from utils import (
    get_element_size, create_buffer, create_multiple_buffers,
    bytes_to_hex_safe_fixed, hex_to_bytes_safe, validate_index, find_matching_key
)


class CryptoServices:
    """High-level cryptographic operations."""
    
    @staticmethod
    def setup_system(param_file: str) -> Dict:
        """Initialize the cryptographic system."""
        full_path = config.validate_param_file(param_file)
        
        print(f"🔧 Initializing with {full_path}")
        result = stealth_lib.init(full_path)
        
        if result != 0:
            raise Exception(f"Library initialization failed with code: {result}")
        
        if not stealth_lib.is_initialized():
            raise Exception("Library initialization verification failed")
        
        # Update configuration
        config.dsk_functions_available = stealth_lib.dsk_functions_available
        
        # Clear existing data first
        config.reset()
        
        # Generate trace key (pass param_file since config is reset)
        trace_key = CryptoServices._generate_trace_key_with_param(param_file)
        config.set_initialized(param_file, trace_key)
        
        g1_size, zr_size = stealth_lib.get_element_sizes()
        
        return {
            "status": "setup complete",
            "message": f"System initialized with {param_file}",
            "param_file": param_file,
            "g1_size": g1_size,
            "zr_size": zr_size,
            "dsk_functions_available": config.dsk_functions_available,
            **trace_key
        }
    
    @staticmethod
    def _generate_trace_key_with_param(param_file: str) -> Dict:
        """Generate trace key pair with specific param file."""
        # Get element size directly from library since system might not be marked as initialized yet
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
    
    @staticmethod
    def generate_trace_key() -> Dict:
        """Generate trace key pair."""
        # Get element size directly from library since system might not be marked as initialized yet
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
            "param_file": config.current_param_file,
            "status": "initialized"
        }
    
    @staticmethod
    def generate_keypair() -> Dict:
        """Generate a new key pair."""
        config.ensure_initialized()
        
        buf_size = get_element_size()
        A_buf, B_buf, a_buf, b_buf = create_multiple_buffers(4, buf_size)
        
        stealth_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
        
        A_hex = bytes_to_hex_safe_fixed(A_buf, 'G1')
        B_hex = bytes_to_hex_safe_fixed(B_buf, 'G1')
        a_hex = bytes_to_hex_safe_fixed(a_buf, 'Zr')
        b_hex = bytes_to_hex_safe_fixed(b_buf, 'Zr')
        
        if not all([A_hex, B_hex, a_hex, b_hex]):
            raise Exception("Failed to generate key pair")
        
        item = {
            "index": len(config.key_list),
            "id": f"key_{len(config.key_list)}",
            "A_hex": A_hex,
            "B_hex": B_hex,
            "a_hex": a_hex,
            "b_hex": b_hex,
            "param_file": config.current_param_file,
            "status": "generated"
        }
        
        config.key_list.append(item)
        return item
    
    @staticmethod
    def generate_address(key_index: int) -> Dict:
        """Generate stealth address with selected key."""
        config.ensure_initialized()
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
        
        stealth_lib.addr_gen(A_bytes, B_bytes, TK_bytes,
                           addr_buf, r1_buf, r2_buf, c_buf, buf_size)
        
        addr_hex = bytes_to_hex_safe_fixed(addr_buf, 'G1')
        r1_hex = bytes_to_hex_safe_fixed(r1_buf, 'G1')
        r2_hex = bytes_to_hex_safe_fixed(r2_buf, 'G1')
        c_hex = bytes_to_hex_safe_fixed(c_buf, 'G1')
        
        if not all([addr_hex, r1_hex, r2_hex, c_hex]):
            raise Exception("Failed to generate address")
        
        address_item = {
            "index": len(config.address_list),
            "id": f"addr_{len(config.address_list)}",
            "addr_hex": addr_hex,
            "r1_hex": r1_hex,
            "r2_hex": r2_hex,
            "c_hex": c_hex,
            "key_index": key_index,
            "key_id": selected_key['id'],
            "owner_A": A_hex,
            "owner_B": B_hex,
            "status": "generated"
        }
        
        config.address_list.append(address_item)
        return address_item
    
    @staticmethod
    def verify_address(address_index: int, key_index: int) -> Dict:
        """Verify address with selected key."""
        config.ensure_initialized()
        validate_index(address_index, config.address_list, "address_index")
        validate_index(key_index, config.key_list, "key_index")
        
        address_data = config.address_list[address_index]
        key_data = config.key_list[key_index]
        
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        b_bytes = hex_to_bytes_safe(key_data['B_hex'])
        a_bytes = hex_to_bytes_safe(key_data['A_hex'])
        c_bytes = hex_to_bytes_safe(address_data['c_hex'])
        a_priv_bytes = hex_to_bytes_safe(key_data['a_hex'])
        
        result = stealth_lib.addr_verify(r1_bytes, b_bytes, a_bytes, c_bytes, a_priv_bytes)
        
        return {
            "valid": result,
            "address_index": address_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "is_owner": (address_data['key_index'] == key_index),
            "status": "valid" if result else "invalid"
        }
    
    @staticmethod
    def generate_dsk(address_index: int, key_index: int) -> Dict:
        """Generate DSK for selected address and key."""
        config.ensure_initialized()
        validate_index(address_index, config.address_list, "address_index")
        validate_index(key_index, config.key_list, "key_index")
        
        address_data = config.address_list[address_index]
        key_data = config.key_list[key_index]
        
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        a_bytes = hex_to_bytes_safe(key_data['a_hex'])
        b_bytes = hex_to_bytes_safe(key_data['b_hex'])
        
        buf_size = get_element_size()
        dsk_buf = create_buffer(buf_size)
        
        if config.dsk_functions_available:
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
            "method": method,
            "status": "generated"
        }
        
        config.dsk_list.append(dsk_item)
        return dsk_item
    
    @staticmethod
    def sign_message(message: str, dsk_index: Optional[int] = None, 
                    address_index: Optional[int] = None, key_index: Optional[int] = None) -> Dict:
        """Sign message with DSK or key pair."""
        config.ensure_initialized()
        message_bytes = message.encode('utf-8')
        
        if dsk_index is not None:
            return CryptoServices._sign_with_dsk(message, message_bytes, dsk_index)
        elif address_index is not None and key_index is not None:
            return CryptoServices._sign_with_keypair(message, message_bytes, address_index, key_index)
        else:
            raise ValueError("Must specify either dsk_index or (address_index and key_index)")
    
    @staticmethod
    def _sign_with_dsk(message: str, message_bytes: bytes, dsk_index: int) -> Dict:
        """Sign message with DSK."""
        validate_index(dsk_index, config.dsk_list, "dsk_index")
        
        if not config.dsk_functions_available:
            raise Exception("DSK signing not available in fallback mode")
        
        dsk_data = config.dsk_list[dsk_index]
        address_data = config.address_list[dsk_data['address_index']]
        
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        dsk_bytes = hex_to_bytes_safe(dsk_data['dsk_hex'])
        
        buf_size = get_element_size()
        q_sigma_buf, h_buf = create_multiple_buffers(2, buf_size)
        
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
            "address_id": dsk_data['address_id'],
            "method": "dsk",
            "status": "signed"
        }
    
    @staticmethod
    def _sign_with_keypair(message: str, message_bytes: bytes, address_index: int, key_index: int) -> Dict:
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
    
    @staticmethod
    def verify_signature(message: str, q_sigma_hex: str, h_hex: str, address_index: int) -> Dict:
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
        
        result = stealth_lib.verify(addr_bytes, r2_bytes, c_bytes, message_bytes, h_bytes, q_sigma_bytes)
        
        return {
            "valid": result,
            "message": message,
            "address_index": address_index,
            "address_id": address_data['id'],
            "status": "verified" if result else "invalid"
        }
    
    @staticmethod
    def trace_identity(address_index: int) -> Dict:
        """Trace identity for selected address."""
        config.ensure_initialized()
        validate_index(address_index, config.address_list, "address_index")
        
        if config.trace_key is None:
            raise Exception("Trace key not initialized")
        
        address_data = config.address_list[address_index]
        
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        r2_bytes = hex_to_bytes_safe(address_data['r2_hex'])
        c_bytes = hex_to_bytes_safe(address_data['c_hex'])
        k_bytes = hex_to_bytes_safe(config.trace_key['k_hex'])
        
        buf_size = get_element_size()
        b_recovered_buf = create_buffer(buf_size)
        
        stealth_lib.trace(addr_bytes, r1_bytes, r2_bytes, c_bytes, k_bytes,
                        b_recovered_buf, buf_size)
        
        b_recovered_hex = bytes_to_hex_safe_fixed(b_recovered_buf, 'G1')
        
        if not b_recovered_hex:
            raise Exception("Failed to trace identity")
        
        # Find matching key
        matched_key = find_matching_key(b_recovered_hex)
        
        return {
            "recovered_b_hex": b_recovered_hex,
            "address_index": address_index,
            "address_id": address_data['id'],
            "original_owner": {
                "key_index": address_data['key_index'],
                "key_id": address_data['key_id'],
                "B_hex": address_data['owner_B']
            },
            "matched_key": matched_key,
            "perfect_match": matched_key is not None,
            "status": "traced"
        }
    
    @staticmethod
    def performance_test(iterations: int = 100) -> Dict:
        """Run performance test."""
        config.ensure_initialized()
        
        # Limit iterations to prevent excessive load
        iterations = min(iterations, 1000)
        
        # Create results array
        from ctypes import c_double
        results = (c_double * 7)()
        
        stealth_lib.performance_test(iterations, results)
        
        return {
            "iterations": iterations,
            "addr_gen_ms": round(results[0], 3),
            "addr_verify_ms": round(results[1], 3),
            "fast_verify_ms": round(results[2], 3),
            "sign_ms": round(results[4], 3),
            "sig_verify_ms": round(results[5], 3),
            "trace_ms": round(results[6], 3),
            "onetime_sk_ms": round(results[3], 3),
            "status": "completed"
        }