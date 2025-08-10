#!/usr/bin/env python3
"""
Test single address generation with detailed debugging
"""
from sitaiba_library_wrapper import sitaiba_lib
from sitaiba_utils import *

def test_single_generation():
    print("🔍 Testing Single Address Generation")
    print("====================================")
    
    # Initialize
    sitaiba_lib.init("../param/pbc/a.param")
    
    buf_size = get_sitaiba_element_size()
    print(f"Buffer size: {buf_size}")
    
    # Generate user keys
    A_buf, B_buf, a_buf, b_buf = create_multiple_sitaiba_buffers(4, buf_size)
    sitaiba_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
    
    A_hex = bytes_to_hex_safe_fixed_sitaiba(A_buf, 'G1')
    B_hex = bytes_to_hex_safe_fixed_sitaiba(B_buf, 'G1')
    
    print(f"Generated keys:")
    print(f"  A first 20 bytes: {list(A_buf[:20])}")
    print(f"  B first 20 bytes: {list(B_buf[:20])}")
    
    # Get tracer key
    A_m_buf = create_sitaiba_buffer(buf_size)
    sitaiba_lib.get_tracer_public_key(A_m_buf, buf_size)
    A_m_hex = bytes_to_hex_safe_fixed_sitaiba(A_m_buf, 'G1')
    
    print(f"  A_m first 20 bytes: {list(A_m_buf[:20])}")
    
    # Convert to bytes for API call
    A_bytes = hex_to_bytes_safe_sitaiba(A_hex)
    B_bytes = hex_to_bytes_safe_sitaiba(B_hex) 
    A_m_bytes = hex_to_bytes_safe_sitaiba(A_m_hex)
    
    print(f"Converted to bytes:")
    print(f"  A_bytes first 20: {list(A_bytes[:20])}")
    print(f"  B_bytes first 20: {list(B_bytes[:20])}")
    print(f"  A_m_bytes first 20: {list(A_m_bytes[:20])}")
    
    # Generate address
    print(f"\nCalling addr_gen...")
    addr_buf, r1_buf, r2_buf = create_multiple_sitaiba_buffers(3, buf_size)
    sitaiba_lib.addr_gen(A_bytes, B_bytes, A_m_bytes, addr_buf, r1_buf, r2_buf, buf_size)
    
    print(f"Results:")
    print(f"  r2_buf first 20 bytes: {list(r2_buf[:20])}")
    
if __name__ == "__main__":
    test_single_generation()