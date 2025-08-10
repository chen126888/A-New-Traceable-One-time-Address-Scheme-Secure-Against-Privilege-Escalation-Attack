#!/usr/bin/env python3
"""
Test SITAIBA message signing functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schemes.sitaiba_scheme import SitaibaScheme

def test_message_signing():
    print("🔍 Testing SITAIBA Message Signing")
    print("==================================")
    
    # Initialize scheme
    scheme = SitaibaScheme()
    setup_result = scheme.setup_system("a.param")
    
    # Generate a key pair
    key_result = scheme.generate_keypair()
    print(f"Generated key: {key_result['id']}")
    
    # Generate an address (needed for DSK generation which is used for signing)
    addr_result = scheme.generate_address(0)
    print(f"Generated address: {addr_result['id']}")
    
    # Test message signing
    message = "Hello, SITAIBA world!"
    
    try:
        sign_result = scheme.sign_message(message=message, key_index=0)
        
        print(f"\n📝 Message signing:")
        print(f"  Message: {message}")
        print(f"  Signature ID: {sign_result['signature']['id']}")
        print(f"  Status: {sign_result['status']}")
        print(f"  DSK (signature): {sign_result['signature']['dsk_hex'][:50]}...")
        
        # Test signature verification
        verify_result = scheme.verify_signature(signature_index=0)
        
        print(f"\n🔐 Signature verification:")
        print(f"  Valid: {verify_result['valid']}")
        print(f"  Status: {verify_result['status']}")
        print(f"  Method: {verify_result['verification_method']}")
        
        if verify_result['valid']:
            print("✅ SUCCESS: Message signing and verification works!")
            return True
        else:
            print("❌ FAILURE: Signature verification failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in message signing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_message_signing()
    exit(0 if success else 1)