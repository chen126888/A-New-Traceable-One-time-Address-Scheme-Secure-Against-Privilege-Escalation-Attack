#!/usr/bin/env python3
"""
Test individual SITAIBA API interfaces to find errors
"""
from sitaiba_library_wrapper import sitaiba_lib
from sitaiba_utils import *

def test_library_basic():
    print("🔧 Testing basic library functions...")
    
    # Test initialization
    result = sitaiba_lib.init("../param/pbc/a.param")
    print(f"   Init result: {result}")
    
    # Test is_initialized
    initialized = sitaiba_lib.is_initialized()
    print(f"   Is initialized: {initialized}")
    
    # Test element sizes
    g1_size, zr_size = sitaiba_lib.get_element_sizes()
    print(f"   G1 size: {g1_size}, Zr size: {zr_size}")
    
    return initialized

def test_key_generation():
    print("\n🔑 Testing key generation...")
    
    buf_size = get_sitaiba_element_size()
    print(f"   Buffer size: {buf_size}")
    
    # Create buffers
    A_buf, B_buf, a_buf, b_buf = create_multiple_sitaiba_buffers(4, buf_size)
    
    # Generate key
    sitaiba_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
    
    # Convert to hex
    A_hex = bytes_to_hex_safe_fixed_sitaiba(A_buf, 'G1')
    B_hex = bytes_to_hex_safe_fixed_sitaiba(B_buf, 'G1')
    a_hex = bytes_to_hex_safe_fixed_sitaiba(a_buf, 'Zr')
    b_hex = bytes_to_hex_safe_fixed_sitaiba(b_buf, 'Zr')
    
    print(f"   A_hex length: {len(A_hex) if A_hex else 0}")
    print(f"   B_hex length: {len(B_hex) if B_hex else 0}")
    print(f"   a_hex length: {len(a_hex) if a_hex else 0}")
    print(f"   b_hex length: {len(b_hex) if b_hex else 0}")
    
    return all([A_hex, B_hex, a_hex, b_hex]), (A_hex, B_hex, a_hex, b_hex)

def test_tracer_key():
    print("\n🔍 Testing tracer key access...")
    
    buf_size = get_sitaiba_element_size()
    A_m_buf = create_sitaiba_buffer(buf_size)
    
    # Get tracer public key
    result = sitaiba_lib.get_tracer_public_key(A_m_buf, buf_size)
    print(f"   Get tracer key result: {result}")
    
    A_m_hex = bytes_to_hex_safe_fixed_sitaiba(A_m_buf, 'G1')
    print(f"   A_m hex length: {len(A_m_hex) if A_m_hex else 0}")
    
    return result == 0, A_m_hex

def test_address_generation(user_keys, tracer_key):
    print("\n🏠 Testing address generation...")
    
    A_hex, B_hex, a_hex, b_hex = user_keys
    A_m_hex = tracer_key
    
    # Convert hex back to bytes
    try:
        A_bytes = hex_to_bytes_safe_sitaiba(A_hex)
        B_bytes = hex_to_bytes_safe_sitaiba(B_hex)
        print(f"   Hex to bytes conversion: OK")
    except Exception as e:
        print(f"   Hex to bytes conversion failed: {e}")
        return False, None
    
    buf_size = get_sitaiba_element_size()
    addr_buf, r1_buf, r2_buf = create_multiple_sitaiba_buffers(3, buf_size)
    
    # Generate address (using None for internal tracer key)
    sitaiba_lib.addr_gen(A_bytes, B_bytes, None, addr_buf, r1_buf, r2_buf, buf_size)
    
    # Convert to hex
    addr_hex = bytes_to_hex_safe_fixed_sitaiba(addr_buf, 'G1')
    r1_hex = bytes_to_hex_safe_fixed_sitaiba(r1_buf, 'G1')
    r2_hex = bytes_to_hex_safe_fixed_sitaiba(r2_buf, 'G1')
    
    print(f"   Addr hex length: {len(addr_hex) if addr_hex else 0}")
    print(f"   R1 hex length: {len(r1_hex) if r1_hex else 0}")
    print(f"   R2 hex length: {len(r2_hex) if r2_hex else 0}")
    
    success = all([addr_hex, r1_hex, r2_hex])
    return success, (addr_hex, r1_hex, r2_hex)

def test_address_verification(user_keys, address_data):
    print("\n✅ Testing address verification...")
    
    A_hex, B_hex, a_hex, b_hex = user_keys
    addr_hex, r1_hex, r2_hex = address_data
    
    # Convert to bytes
    try:
        addr_bytes = hex_to_bytes_safe_sitaiba(addr_hex)
        r1_bytes = hex_to_bytes_safe_sitaiba(r1_hex)
        r2_bytes = hex_to_bytes_safe_sitaiba(r2_hex)
        A_bytes = hex_to_bytes_safe_sitaiba(A_hex)
        B_bytes = hex_to_bytes_safe_sitaiba(B_hex)
        a_bytes = hex_to_bytes_safe_sitaiba(a_hex)
        print(f"   All hex to bytes conversions: OK")
    except Exception as e:
        print(f"   Hex to bytes conversion failed: {e}")
        return False
    
    # Verify address (using None for internal tracer key)
    result = sitaiba_lib.addr_verify(addr_bytes, r1_bytes, r2_bytes, 
                                   A_bytes, B_bytes, a_bytes, None)
    
    print(f"   Verification result: {result}")
    return result

def test_tracing(user_keys, address_data):
    print("\n🕵️ Testing identity tracing...")
    
    A_hex, B_hex, a_hex, b_hex = user_keys
    addr_hex, r1_hex, r2_hex = address_data
    
    # Convert to bytes
    try:
        addr_bytes = hex_to_bytes_safe_sitaiba(addr_hex)
        r1_bytes = hex_to_bytes_safe_sitaiba(r1_hex)
        r2_bytes = hex_to_bytes_safe_sitaiba(r2_hex)
    except Exception as e:
        print(f"   Hex to bytes conversion failed: {e}")
        return False, None
    
    buf_size = get_sitaiba_element_size()
    B_recovered_buf = create_sitaiba_buffer(buf_size)
    
    # Trace identity (using None for internal tracer private key)
    sitaiba_lib.trace(addr_bytes, r1_bytes, r2_bytes, None, B_recovered_buf, buf_size)
    
    # Convert to hex
    B_recovered_hex = bytes_to_hex_safe_fixed_sitaiba(B_recovered_buf, 'G1')
    print(f"   Recovered B_hex length: {len(B_recovered_hex) if B_recovered_hex else 0}")
    print(f"   Original  B_hex: {B_hex[:50]}...")
    print(f"   Recovered B_hex: {B_recovered_hex[:50] if B_recovered_hex else 'None'}...")
    
    match = B_recovered_hex == B_hex if B_recovered_hex else False
    print(f"   Perfect match: {match}")
    
    return match, B_recovered_hex

def main():
    print("🧪 Testing SITAIBA API Interfaces")
    print("=================================")
    
    # Test 1: Basic library functions
    if not test_library_basic():
        print("❌ Basic library test failed")
        return False
    
    # Test 2: Key generation
    key_success, user_keys = test_key_generation()
    if not key_success:
        print("❌ Key generation test failed")
        return False
    
    # Test 3: Tracer key access
    tracer_success, tracer_key = test_tracer_key()
    if not tracer_success:
        print("❌ Tracer key test failed")
        return False
    
    # Test 4: Address generation
    addr_success, address_data = test_address_generation(user_keys, tracer_key)
    if not addr_success:
        print("❌ Address generation test failed")
        return False
    
    # Test 5: Address verification
    verify_success = test_address_verification(user_keys, address_data)
    if not verify_success:
        print("❌ Address verification test failed")
        return False
    
    # Test 6: Identity tracing
    trace_success, recovered = test_tracing(user_keys, address_data)
    if not trace_success:
        print("❌ Identity tracing test failed")
        return False
    
    print("\n🎉 All API interface tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)