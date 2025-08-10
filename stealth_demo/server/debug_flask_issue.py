#!/usr/bin/env python3

import sys
sys.path.append('/mnt/c/Users/chen1/Desktop/master/thesis/nccu/new/code/stealth_demo/server')

from schemes.scheme_manager import scheme_manager
from schemes.sitaiba_scheme import SitaibaScheme

def main():
    print("🐛 Debugging Flask API vs Direct API issue")
    print("=" * 50)
    
    # Use global scheme manager (same as Flask app)
    manager = scheme_manager
    
    # Register and activate SITAIBA (same as Flask app)
    print("1. Registering and activating SITAIBA scheme...")
    manager.register_scheme(SitaibaScheme)
    manager.activate_scheme("sitaiba")
    setup_result = manager.setup_system(param_file="a.param")
    print(f"   Setup result: {setup_result}")
    
    # Generate key
    print("2. Generating key...")
    key_result = manager.generate_keypair(num_keys=1)
    print(f"   Key result: {key_result}")
    
    # Generate address 
    print("3. Generating address...")
    addr_result = manager.generate_address(key_index=0, num_addresses=1)
    print(f"   Address result: {addr_result}")
    
    # Verify address - this is where the problem occurs
    print("4. Verifying address...")
    verify_result = manager.verify_address(address_index=0, key_index=0)
    print(f"   Verify result: {verify_result}")
    
    # Trace identity
    print("5. Tracing identity...")
    trace_result = manager.trace_identity(address_index=0)
    print(f"   Trace result: {trace_result}")
    
    print("\n🎯 Analysis complete!")

if __name__ == "__main__":
    main()