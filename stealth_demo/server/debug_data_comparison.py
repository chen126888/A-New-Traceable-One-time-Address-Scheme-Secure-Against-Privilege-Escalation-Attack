#!/usr/bin/env python3

import sys
sys.path.append('/mnt/c/Users/chen1/Desktop/master/thesis/nccu/new/code/stealth_demo/server')

from sitaiba_library_wrapper import SitaibaLibrary
from sitaiba_utils import hex_to_bytes_safe_sitaiba, bytes_to_hex_safe_fixed_sitaiba

def test_direct_library():
    """Test the direct library interface like the working test_api_interfaces.py"""
    print("🔍 Testing Direct Library Interface")
    print("=" * 50)
    
    lib = SitaibaLibrary()
    
    # Initialize
    param_file = "/mnt/c/Users/chen1/Desktop/master/thesis/nccu/new/code/stealth_demo/param/pbc/a.param"
    init_result = lib.init(param_file)
    print(f"Init result: {init_result}")
    
    # Generate key
    A_buf = bytearray(512)
    B_buf = bytearray(512)  
    a_buf = bytearray(512)
    b_buf = bytearray(512)
    
    keygen_result = lib.keygen(A_buf, B_buf, a_buf, b_buf, 512)
    print(f"Key generation result: {keygen_result}")
    
    # Convert to hex for display
    A_hex = bytes_to_hex_safe_fixed_sitaiba(A_buf, 128)
    B_hex = bytes_to_hex_safe_fixed_sitaiba(B_buf, 128) 
    a_hex = bytes_to_hex_safe_fixed_sitaiba(a_buf, 20)
    b_hex = bytes_to_hex_safe_fixed_sitaiba(b_buf, 20)
    
    print(f"A_hex: {A_hex}")
    print(f"B_hex: {B_hex}")
    print(f"a_hex: {a_hex}")
    print(f"b_hex: {b_hex}")
    
    # Generate address
    addr_buf = bytearray(512)
    r1_buf = bytearray(512)
    r2_buf = bytearray(512)
    
    # Convert hex back to bytes for address generation
    A_bytes = hex_to_bytes_safe_sitaiba(A_hex)
    B_bytes = hex_to_bytes_safe_sitaiba(B_hex)
    a_bytes = hex_to_bytes_safe_sitaiba(a_hex)
    
    addrgen_result = lib.addrgen(A_bytes, B_bytes, a_bytes, None, addr_buf, r1_buf, r2_buf, 512)
    print(f"Address generation result: {addrgen_result}")
    
    # Convert address components to hex
    addr_hex = bytes_to_hex_safe_fixed_sitaiba(addr_buf, 128)
    r1_hex = bytes_to_hex_safe_fixed_sitaiba(r1_buf, 128)
    r2_hex = bytes_to_hex_safe_fixed_sitaiba(r2_buf, 128)
    
    print(f"Address: {addr_hex}")
    print(f"R1: {r1_hex}")
    print(f"R2: {r2_hex}")
    
    # Test address verification - convert hex back to bytes
    addr_bytes = hex_to_bytes_safe_sitaiba(addr_hex)
    r1_bytes = hex_to_bytes_safe_sitaiba(r1_hex)
    r2_bytes = hex_to_bytes_safe_sitaiba(r2_hex)
    A_bytes = hex_to_bytes_safe_sitaiba(A_hex)
    B_bytes = hex_to_bytes_safe_sitaiba(B_hex)
    a_bytes = hex_to_bytes_safe_sitaiba(a_hex)
    
    verify_result = lib.addr_verify(addr_bytes, r1_bytes, r2_bytes, A_bytes, B_bytes, a_bytes, None)
    print(f"✅ Verification result: {verify_result}")
    
    # Test identity tracing
    recovered_buf = bytearray(512)
    trace_result = lib.identity_tracing(addr_bytes, r1_bytes, r2_bytes, recovered_buf, 512)
    print(f"Trace result: {trace_result}")
    
    recovered_hex = bytes_to_hex_safe_fixed_sitaiba(recovered_buf, 128)
    print(f"Original B_hex:  {B_hex}")
    print(f"Recovered B_hex: {recovered_hex}")
    print(f"✅ Perfect match: {B_hex == recovered_hex}")
    
    return {
        'A_hex': A_hex, 'B_hex': B_hex, 'a_hex': a_hex, 'b_hex': b_hex,
        'addr_hex': addr_hex, 'r1_hex': r1_hex, 'r2_hex': r2_hex,
        'verify_result': verify_result,
        'recovered_hex': recovered_hex,
        'perfect_match': B_hex == recovered_hex
    }

if __name__ == "__main__":
    result = test_direct_library()
    print(f"\n🎯 Direct library test summary:")
    print(f"   Verification: {result['verify_result']}")  
    print(f"   Perfect match: {result['perfect_match']}")