#!/usr/bin/env python3
"""
Test script to debug the trace issue by comparing C core and Python API results
"""
import sys
import os
sys.path.append('/mnt/c/Users/chen1/Desktop/master/thesis/nccu/new/code/stealth_demo/server')

from sitaiba_library_wrapper import SitaibaLibrary
from sitaiba_utils import *

def test_trace_consistency():
    """Test if tracing produces consistent results"""
    
    print("🧪 Testing SITAIBA Trace Consistency")
    print("===================================\n")
    
    # Use the pre-loaded library
    lib = sitaiba_lib
    
    # Check if already initialized
    if lib.is_initialized():
        print("✅ SITAIBA already initialized")
    else:
        param_file = '/mnt/c/Users/chen1/Desktop/master/thesis/nccu/new/code/stealth_demo/param/pbc/a.param'
        if lib.init(param_file) != 1:
            print("❌ Failed to initialize SITAIBA")
            return
        print("✅ SITAIBA initialized successfully")
    
    # Generate user key
    buf_size = lib.get_element_sizes()[0]  # G1 size
    A_buf, B_buf, a_buf, b_buf = create_multiple_sitaiba_buffers(4, buf_size)
    lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
    
    A_hex = bytes_to_hex_safe_fixed_sitaiba(A_buf, 'G1')
    B_hex = bytes_to_hex_safe_fixed_sitaiba(B_buf, 'G1')
    a_hex = bytes_to_hex_safe_fixed_sitaiba(a_buf, 'Zr')
    b_hex = bytes_to_hex_safe_fixed_sitaiba(b_buf, 'Zr')
    
    print(f"Generated user key:")
    print(f"  B: {B_hex[:50]}...")
    
    # Generate address
    A_bytes = hex_to_bytes_safe_sitaiba(A_hex)
    B_bytes = hex_to_bytes_safe_sitaiba(B_hex)
    
    addr_buf, r1_buf, r2_buf = create_multiple_sitaiba_buffers(3, buf_size)
    lib.addr_gen(A_bytes, B_bytes, None, addr_buf, r1_buf, r2_buf, buf_size)
    
    addr_hex = bytes_to_hex_safe_fixed_sitaiba(addr_buf, 'G1')
    r1_hex = bytes_to_hex_safe_fixed_sitaiba(r1_buf, 'G1')
    r2_hex = bytes_to_hex_safe_fixed_sitaiba(r2_buf, 'G1')
    
    print(f"Generated address:")
    print(f"  Addr: {addr_hex[:50]}...")
    print(f"  R1: {r1_hex[:50]}...")
    print(f"  R2: {r2_hex[:50]}...")
    
    # Test tracing
    addr_bytes = hex_to_bytes_safe_sitaiba(addr_hex)
    r1_bytes = hex_to_bytes_safe_sitaiba(r1_hex)
    r2_bytes = hex_to_bytes_safe_sitaiba(r2_hex)
    
    b_recovered_buf = create_sitaiba_buffer(buf_size)
    lib.trace(addr_bytes, r1_bytes, r2_bytes, None, b_recovered_buf, buf_size)
    
    b_recovered_hex = bytes_to_hex_safe_fixed_sitaiba(b_recovered_buf, 'G1')
    
    print(f"Trace result:")
    print(f"  Original B: {B_hex[:50]}...")
    print(f"  Recovered B: {b_recovered_hex[:50]}...")
    print(f"  Match: {'✅ YES' if B_hex == b_recovered_hex else '❌ NO'}")
    
    # Test verification
    a_bytes = hex_to_bytes_safe_sitaiba(a_hex)
    verify_result = lib.addr_verify(addr_bytes, r1_bytes, r2_bytes, A_bytes, B_bytes, a_bytes, None)
    
    print(f"Verification result: {'✅ VALID' if verify_result else '❌ INVALID'}")
    
    return B_hex == b_recovered_hex and verify_result

if __name__ == "__main__":
    success = test_trace_consistency()
    print(f"\n{'🎉 Test PASSED!' if success else '❌ Test FAILED!'}")