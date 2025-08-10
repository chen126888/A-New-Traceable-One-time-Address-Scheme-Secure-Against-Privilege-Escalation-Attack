#!/usr/bin/env python3
"""
Test R2 generation specifically to debug why R2 becomes zero
"""
from sitaiba_library_wrapper import sitaiba_lib
from sitaiba_utils import *

def test_r2_generation():
    print("🔍 Testing R2 Generation")
    print("========================")
    
    # Initialize
    sitaiba_lib.init("../param/pbc/a.param")
    
    buf_size = get_sitaiba_element_size()
    
    # Generate user keys
    A_buf, B_buf, a_buf, b_buf = create_multiple_sitaiba_buffers(4, buf_size)
    sitaiba_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
    
    A_hex = bytes_to_hex_safe_fixed_sitaiba(A_buf, 'G1')
    B_hex = bytes_to_hex_safe_fixed_sitaiba(B_buf, 'G1')
    
    # Get tracer key
    A_m_buf = create_sitaiba_buffer(buf_size)
    sitaiba_lib.get_tracer_public_key(A_m_buf, buf_size)
    A_m_hex = bytes_to_hex_safe_fixed_sitaiba(A_m_buf, 'G1')
    
    print(f"Keys generated successfully")
    print(f"  A: {A_hex[:30]}...")
    print(f"  B: {B_hex[:30]}...")
    print(f"  A_m: {A_m_hex[:30]}...")
    
    # Test multiple address generations
    for i in range(3):
        print(f"\n--- Generation {i+1} ---")
        
        A_bytes = hex_to_bytes_safe_sitaiba(A_hex)
        B_bytes = hex_to_bytes_safe_sitaiba(B_hex)
        A_m_bytes = hex_to_bytes_safe_sitaiba(A_m_hex)
        
        addr_buf, r1_buf, r2_buf = create_multiple_sitaiba_buffers(3, buf_size)
        
        # Check buffers before generation
        print(f"Before generation:")
        print(f"  addr_buf all zero: {all(b == 0 for b in addr_buf)}")
        print(f"  r1_buf all zero: {all(b == 0 for b in r1_buf)}")
        print(f"  r2_buf all zero: {all(b == 0 for b in r2_buf)}")
        
        # Generate address
        sitaiba_lib.addr_gen(A_bytes, B_bytes, A_m_bytes, addr_buf, r1_buf, r2_buf, buf_size)
        
        # Check buffers after generation
        print(f"After generation:")
        print(f"  addr_buf all zero: {all(b == 0 for b in addr_buf)}")
        print(f"  r1_buf all zero: {all(b == 0 for b in r1_buf)}")
        print(f"  r2_buf all zero: {all(b == 0 for b in r2_buf)}")
        
        # Convert to hex for display
        addr_hex = bytes_to_hex_safe_fixed_sitaiba(addr_buf, 'G1')
        r1_hex = bytes_to_hex_safe_fixed_sitaiba(r1_buf, 'G1')
        r2_hex = bytes_to_hex_safe_fixed_sitaiba(r2_buf, 'G1')
        
        print(f"Hex representations:")
        print(f"  Addr: {addr_hex[:30]}...")
        print(f"  R1: {r1_hex[:30]}...")
        print(f"  R2: {r2_hex[:30]}...")
        
        # Check raw bytes
        print(f"First 20 bytes of r2_buf: {list(r2_buf[:20])}")

if __name__ == "__main__":
    test_r2_generation()