#!/usr/bin/env python3
"""
Test the fixed API to ensure R2 is no longer zero
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schemes.sitaiba_scheme import SitaibaScheme

def test_sitaiba_fix():
    print("🔍 Testing SITAIBA Fix")
    print("======================")
    
    # Initialize scheme
    scheme = SitaibaScheme()
    setup_result = scheme.setup_system("a.param")
    
    print(f"Setup result: {setup_result}")
    print(f"Tracer key available: {setup_result.get('tracer_key', 'N/A')}")
    
    # Generate a key pair
    key_result = scheme.generate_keypair()
    print(f"\nGenerated key: {key_result['id']}")
    
    # Generate address using the fixed implementation
    addr_result = scheme.generate_address(0)  # Use first key
    
    print(f"\nGenerated address:")
    print(f"  ID: {addr_result['id']}")
    print(f"  Addr: {addr_result['addr_hex'][:50]}...")
    print(f"  R1: {addr_result['r1_hex'][:50]}...")
    print(f"  R2: {addr_result['r2_hex'][:50]}...")
    
    # Check if R2 is all zeros
    r2_hex = addr_result['r2_hex']
    is_r2_zero = r2_hex == '0' * len(r2_hex)
    
    print(f"\n✅ R2 is zero: {is_r2_zero}")
    print(f"✅ R2 length: {len(r2_hex)}")
    print(f"✅ R2 first 30 chars: {r2_hex[:30]}")
    
    if not is_r2_zero:
        print("🎉 SUCCESS: R2 is no longer all zeros!")
        
        # Test verification
        verify_result = scheme.verify_address(0, 0)  # Verify with same key
        print(f"\n🔐 Verification result: {verify_result['valid']}")
        print(f"🔐 Verification status: {verify_result['status']}")
        
        return True
    else:
        print("❌ FAILURE: R2 is still all zeros")
        return False

if __name__ == "__main__":
    success = test_sitaiba_fix()
    exit(0 if success else 1)