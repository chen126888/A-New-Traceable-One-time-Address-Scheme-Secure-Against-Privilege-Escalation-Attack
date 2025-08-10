#!/usr/bin/env python3
"""
Debug tracer key consistency between address generation and verification
"""
from sitaiba_library_wrapper import sitaiba_lib
from sitaiba_utils import *

def test_tracer_key_consistency():
    print("🔍 Testing tracer key consistency")
    print("=================================")
    
    # Initialize
    sitaiba_lib.init("../param/pbc/a.param")
    
    buf_size = get_sitaiba_element_size()
    
    # Get tracer key twice to compare
    print("\n1. Getting tracer key (first time)...")
    A_m_buf1 = create_sitaiba_buffer(buf_size)
    result1 = sitaiba_lib.get_tracer_public_key(A_m_buf1, buf_size)
    A_m_hex1 = bytes_to_hex_safe_fixed_sitaiba(A_m_buf1, 'G1')
    print(f"   Result: {result1}, Hex: {A_m_hex1[:50]}...")
    
    print("\n2. Getting tracer key (second time)...")
    A_m_buf2 = create_sitaiba_buffer(buf_size)
    result2 = sitaiba_lib.get_tracer_public_key(A_m_buf2, buf_size)
    A_m_hex2 = bytes_to_hex_safe_fixed_sitaiba(A_m_buf2, 'G1')
    print(f"   Result: {result2}, Hex: {A_m_hex2[:50]}...")
    
    print(f"\n3. Consistency check: {A_m_hex1 == A_m_hex2}")
    
    # Generate user key
    print("\n4. Generating user key...")
    A_buf, B_buf, a_buf, b_buf = create_multiple_sitaiba_buffers(4, buf_size)
    sitaiba_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
    
    A_hex = bytes_to_hex_safe_fixed_sitaiba(A_buf, 'G1')
    B_hex = bytes_to_hex_safe_fixed_sitaiba(B_buf, 'G1')
    a_hex = bytes_to_hex_safe_fixed_sitaiba(a_buf, 'Zr')
    
    # Generate address with explicit tracer key
    print("\n5. Generating address with explicit tracer key...")
    A_bytes = hex_to_bytes_safe_sitaiba(A_hex)
    B_bytes = hex_to_bytes_safe_sitaiba(B_hex)
    A_m_bytes = hex_to_bytes_safe_sitaiba(A_m_hex1)
    
    addr_buf1, r1_buf1, r2_buf1 = create_multiple_sitaiba_buffers(3, buf_size)
    sitaiba_lib.addr_gen(A_bytes, B_bytes, A_m_bytes, addr_buf1, r1_buf1, r2_buf1, buf_size)
    
    addr_hex1 = bytes_to_hex_safe_fixed_sitaiba(addr_buf1, 'G1')
    r1_hex1 = bytes_to_hex_safe_fixed_sitaiba(r1_buf1, 'G1')
    r2_hex1 = bytes_to_hex_safe_fixed_sitaiba(r2_buf1, 'G1')
    print(f"   Address with explicit key: {addr_hex1[:50]}...")
    
    # Generate address with NULL (internal tracer key)
    print("\n6. Generating address with internal tracer key...")
    addr_buf2, r1_buf2, r2_buf2 = create_multiple_sitaiba_buffers(3, buf_size)
    sitaiba_lib.addr_gen(A_bytes, B_bytes, None, addr_buf2, r1_buf2, r2_buf2, buf_size)
    
    addr_hex2 = bytes_to_hex_safe_fixed_sitaiba(addr_buf2, 'G1')
    r1_hex2 = bytes_to_hex_safe_fixed_sitaiba(r1_buf2, 'G1')
    r2_hex2 = bytes_to_hex_safe_fixed_sitaiba(r2_buf2, 'G1')
    print(f"   Address with internal key:  {addr_hex2[:50]}...")
    
    print(f"\n7. Address consistency check: {addr_hex1 == addr_hex2}")
    
    # Verify address with explicit tracer key
    print("\n8. Verifying with explicit tracer key...")
    addr_bytes = hex_to_bytes_safe_sitaiba(addr_hex2)
    r1_bytes = hex_to_bytes_safe_sitaiba(r1_hex2)
    r2_bytes = hex_to_bytes_safe_sitaiba(r2_hex2)
    a_bytes = hex_to_bytes_safe_sitaiba(a_hex)
    
    result_explicit = sitaiba_lib.addr_verify(addr_bytes, r1_bytes, r2_bytes, 
                                            A_bytes, B_bytes, a_bytes, A_m_bytes)
    print(f"   Verification result (explicit): {result_explicit}")
    
    # Verify address with NULL (internal tracer key)
    print("\n9. Verifying with internal tracer key...")
    result_internal = sitaiba_lib.addr_verify(addr_bytes, r1_bytes, r2_bytes, 
                                            A_bytes, B_bytes, a_bytes, None)
    print(f"   Verification result (internal): {result_internal}")
    
    print("\n" + "="*50)
    print("Summary:")
    print(f"   Tracer key consistent: {A_m_hex1 == A_m_hex2}")
    print(f"   Address consistent: {addr_hex1 == addr_hex2}")
    print(f"   Verification (explicit): {result_explicit}")
    print(f"   Verification (internal): {result_internal}")
    
    return all([A_m_hex1 == A_m_hex2, addr_hex1 == addr_hex2, result_explicit, result_internal])

if __name__ == "__main__":
    success = test_tracer_key_consistency()
    exit(0 if success else 1)