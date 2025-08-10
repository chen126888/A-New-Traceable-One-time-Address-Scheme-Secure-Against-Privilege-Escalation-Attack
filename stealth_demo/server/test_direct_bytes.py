#!/usr/bin/env python3
"""
Test direct bytes without hex conversion
"""
from sitaiba_library_wrapper import sitaiba_lib
from sitaiba_utils import *

def test_direct_bytes():
    print("🔍 Testing Direct Bytes (no hex conversion)")
    print("============================================")
    
    # Initialize
    sitaiba_lib.init("../param/pbc/a.param")
    
    buf_size = get_sitaiba_element_size()
    print(f"Buffer size: {buf_size}")
    
    # Generate user keys directly
    A_buf, B_buf, a_buf, b_buf = create_multiple_sitaiba_buffers(4, buf_size)
    sitaiba_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
    
    print(f"Generated keys (direct buffers):")
    print(f"  A first 20 bytes: {list(A_buf[:20])}")
    print(f"  B first 20 bytes: {list(B_buf[:20])}")
    
    # Get tracer key directly  
    A_m_buf = create_sitaiba_buffer(buf_size)
    sitaiba_lib.get_tracer_public_key(A_m_buf, buf_size)
    
    print(f"  A_m first 20 bytes: {list(A_m_buf[:20])}")
    
    # Use direct bytes (no conversion) - convert to bytes() for API
    A_bytes = bytes(A_buf)
    B_bytes = bytes(B_buf)
    A_m_bytes = bytes(A_m_buf)
    
    print(f"Direct bytes (no hex conversion):")
    print(f"  A_bytes first 20: {list(A_bytes[:20])}")
    print(f"  B_bytes first 20: {list(B_bytes[:20])}")
    print(f"  A_m_bytes first 20: {list(A_m_bytes[:20])}")
    
    # Generate address with direct bytes
    print(f"\nCalling addr_gen with direct bytes...")
    addr_buf, r1_buf, r2_buf = create_multiple_sitaiba_buffers(3, buf_size)
    sitaiba_lib.addr_gen(A_bytes, B_bytes, A_m_bytes, addr_buf, r1_buf, r2_buf, buf_size)
    
    print(f"Results:")
    print(f"  Addr first 20 bytes: {list(addr_buf[:20])}")
    print(f"  R1 first 20 bytes: {list(r1_buf[:20])}")
    print(f"  R2 first 20 bytes: {list(r2_buf[:20])}")
    
    # Check if R2 is all zeros
    r2_all_zero = all(b == 0 for b in r2_buf)
    print(f"  R2 is all zero: {r2_all_zero}")

if __name__ == "__main__":
    test_direct_bytes()