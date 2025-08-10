#!/usr/bin/env python3
"""
Compare address verification implementations by creating detailed debug output
"""
from sitaiba_library_wrapper import sitaiba_lib
from sitaiba_utils import *

def debug_verification_steps():
    print("🔍 Debugging Address Verification Steps")
    print("======================================")
    
    # Initialize
    sitaiba_lib.init("../param/pbc/a.param")
    
    buf_size = get_sitaiba_element_size()
    
    # Generate user keys
    A_buf, B_buf, a_buf, b_buf = create_multiple_sitaiba_buffers(4, buf_size)
    sitaiba_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
    
    A_hex = bytes_to_hex_safe_fixed_sitaiba(A_buf, 'G1')
    B_hex = bytes_to_hex_safe_fixed_sitaiba(B_buf, 'G1')
    a_hex = bytes_to_hex_safe_fixed_sitaiba(a_buf, 'Zr')
    b_hex = bytes_to_hex_safe_fixed_sitaiba(b_buf, 'Zr')
    
    # Get tracer key
    A_m_buf = create_sitaiba_buffer(buf_size)
    sitaiba_lib.get_tracer_public_key(A_m_buf, buf_size)
    A_m_hex = bytes_to_hex_safe_fixed_sitaiba(A_m_buf, 'G1')
    
    print(f"User Keys:")
    print(f"  A: {A_hex[:50]}...")
    print(f"  B: {B_hex[:50]}...")
    print(f"  a: {a_hex[:50]}...")
    print(f"  b: {b_hex[:50]}...")
    print(f"Tracer Key:")
    print(f"  A_m: {A_m_hex[:50]}...")
    
    # Generate address
    A_bytes = hex_to_bytes_safe_sitaiba(A_hex)
    B_bytes = hex_to_bytes_safe_sitaiba(B_hex)
    A_m_bytes = hex_to_bytes_safe_sitaiba(A_m_hex)
    
    addr_buf, r1_buf, r2_buf = create_multiple_sitaiba_buffers(3, buf_size)
    sitaiba_lib.addr_gen(A_bytes, B_bytes, A_m_bytes, addr_buf, r1_buf, r2_buf, buf_size)
    
    addr_hex = bytes_to_hex_safe_fixed_sitaiba(addr_buf, 'G1')
    r1_hex = bytes_to_hex_safe_fixed_sitaiba(r1_buf, 'G1')
    r2_hex = bytes_to_hex_safe_fixed_sitaiba(r2_buf, 'G1')
    
    print(f"\nGenerated Address Components:")
    print(f"  Addr: {addr_hex[:50]}...")
    print(f"  R1: {r1_hex[:50]}...")
    print(f"  R2: {r2_hex[:50]}...")
    
    # Test verification
    addr_bytes = hex_to_bytes_safe_sitaiba(addr_hex)
    r1_bytes = hex_to_bytes_safe_sitaiba(r1_hex)
    r2_bytes = hex_to_bytes_safe_sitaiba(r2_hex)
    a_bytes = hex_to_bytes_safe_sitaiba(a_hex)
    
    print(f"\nVerification Tests:")
    
    # Test 1: Full verification with explicit tracer key
    result1 = sitaiba_lib.addr_verify(addr_bytes, r1_bytes, r2_bytes, 
                                     A_bytes, B_bytes, a_bytes, A_m_bytes)
    print(f"  Full verify (explicit tracer): {result1}")
    
    # Test 2: Full verification with internal tracer key
    result2 = sitaiba_lib.addr_verify(addr_bytes, r1_bytes, r2_bytes, 
                                     A_bytes, B_bytes, a_bytes, None)
    print(f"  Full verify (internal tracer): {result2}")
    
    # Test 3: Fast verification
    result3 = sitaiba_lib.addr_verify_fast(r1_bytes, r2_bytes, A_bytes, a_bytes)
    print(f"  Fast verify: {result3}")
    
    # Test different parameter combinations
    print(f"\nParameter Validation:")
    print(f"  All buffers non-zero: {all([any(buf) for buf in [A_bytes, B_bytes, a_bytes, A_m_bytes]])}")
    print(f"  R1 non-zero: {any(r1_bytes)}")
    print(f"  R2 non-zero: {any(r2_bytes)}")
    print(f"  Address non-zero: {any(addr_bytes)}")
    
    return result1, result2, result3

if __name__ == "__main__":
    debug_verification_steps()