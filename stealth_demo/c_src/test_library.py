#!/usr/bin/env python3
"""
Updated test script for stealth library
Tests the separated architecture with core and Python API functions
"""

import sys
import os
from ctypes import *

def test_library_load():
    """Test if library can be loaded"""
    try:
        lib = CDLL("../lib/libstealth.so")
        print("✅ Library loaded successfully")
        return lib
    except Exception as e:
        print(f"❌ Failed to load library: {e}")
        return None

def setup_function_signatures(lib):
    """Setup all function signatures for the library"""
    try:
        # Core library management functions
        lib.stealth_init.argtypes = [c_char_p]
        lib.stealth_init.restype = c_int
        
        lib.stealth_is_initialized.restype = c_int
        lib.stealth_cleanup.restype = None
        lib.stealth_reset_performance.restype = None
        
        lib.stealth_element_size_G1.restype = c_int
        lib.stealth_element_size_Zr.restype = c_int
        
        lib.stealth_get_pairing.restype = c_void_p
        
        # Python interface functions
        lib.stealth_keygen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        lib.stealth_keygen_simple.restype = None
        
        lib.stealth_tracekeygen_simple.argtypes = [c_char_p, c_char_p, c_int]
        lib.stealth_tracekeygen_simple.restype = None
        
        lib.stealth_addr_gen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        lib.stealth_addr_gen_simple.restype = None
        
        lib.stealth_addr_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        lib.stealth_addr_verify_simple.restype = c_int
        
        lib.stealth_sign_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        lib.stealth_sign_simple.restype = None
        
        lib.stealth_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        lib.stealth_verify_simple.restype = c_int
        
        lib.stealth_trace_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        lib.stealth_trace_simple.restype = None
        
        lib.stealth_performance_test_simple.argtypes = [c_int, POINTER(c_double)]
        lib.stealth_performance_test_simple.restype = None
        
        print("✅ Function signatures set up successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up function signatures: {e}")
        return False

def test_initialization(lib):
    """Test library initialization"""
    try:
        # Check initial state
        initialized = lib.stealth_is_initialized()
        print(f"📊 Initial state - Library initialized: {bool(initialized)}")
        
        # Find parameter file
        param_files = [
            "../param/a.param",
            "../param/d159.param", 
            "../param/a1.param"
        ]
        
        param_file = None
        for pf in param_files:
            if os.path.exists(pf):
                param_file = pf
                break
        
        if not param_file:
            print("❌ No parameter file found!")
            print("Available files in param directory:")
            try:
                for f in os.listdir("../param/"):
                    print(f"  📄 {f}")
                # Try first .param file found
                param_files_found = [f for f in os.listdir("../param/") if f.endswith('.param')]
                if param_files_found:
                    param_file = f"../param/{param_files_found[0]}"
                    print(f"🔄 Using: {param_file}")
            except:
                print("❌ Cannot access param directory")
                return False
        
        print(f"🔧 Testing initialization with: {param_file}")
        
        # Initialize library
        result = lib.stealth_init(param_file.encode())
        if result == 0:
            print("✅ Library initialized successfully")
            
            # Check state after initialization
            initialized = lib.stealth_is_initialized()
            print(f"📊 After init - Library initialized: {bool(initialized)}")
            
            # Test element sizes
            g1_size = lib.stealth_element_size_G1()
            zr_size = lib.stealth_element_size_Zr()
            
            print(f"📏 G1 element size: {g1_size} bytes")
            print(f"📏 Zr element size: {zr_size} bytes")
            
            return True
        else:
            print(f"❌ Library initialization failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing initialization: {e}")
        return False

def test_key_generation(lib):
    """Test key generation"""
    try:
        print("\n🔑 Testing Key Generation...")
        
        # Get buffer size
        buf_size = max(lib.stealth_element_size_G1(), lib.stealth_element_size_Zr(), 512)
        print(f"📏 Using buffer size: {buf_size} bytes")
        
        # Create buffers
        A_buf = create_string_buffer(buf_size)
        B_buf = create_string_buffer(buf_size)
        a_buf = create_string_buffer(buf_size)
        b_buf = create_string_buffer(buf_size)
        
        # Generate keys
        lib.stealth_keygen_simple(A_buf, B_buf, a_buf, b_buf, buf_size)
        
        # Check if keys were generated (non-zero)
        A_hex = A_buf.raw[:64].hex()  # Check first 64 bytes
        B_hex = B_buf.raw[:64].hex()
        a_hex = a_buf.raw[:64].hex()
        b_hex = b_buf.raw[:64].hex()
        
        if A_hex != "00" * 32 and B_hex != "00" * 32:
            print("✅ Key generation successful")
            print(f"🔓 Public Key A: {A_hex}...")
            print(f"🔓 Public Key B: {B_hex}...")
            print(f"🔐 Private Key a: {a_hex}...")
            print(f"🔐 Private Key b: {b_hex}...")
            return True, (A_buf, B_buf, a_buf, b_buf)
        else:
            print("❌ Key generation failed - all zeros")
            return False, None
            
    except Exception as e:
        print(f"❌ Error in key generation test: {e}")
        return False, None

def test_trace_key_generation(lib):
    """Test trace key generation"""
    try:
        print("\n🔍 Testing Trace Key Generation...")
        
        buf_size = max(lib.stealth_element_size_G1(), lib.stealth_element_size_Zr(), 512)
        
        # Create buffers
        TK_buf = create_string_buffer(buf_size)
        k_buf = create_string_buffer(buf_size)
        
        # Generate trace key
        lib.stealth_tracekeygen_simple(TK_buf, k_buf, buf_size)
        
        # Check if trace key was generated
        TK_hex = TK_buf.raw[:64].hex()
        k_hex = k_buf.raw[:64].hex()
        
        if TK_hex != "00" * 32 and k_hex != "00" * 32:
            print("✅ Trace key generation successful")
            print(f"🔑 Trace Key TK: {TK_hex}...")
            print(f"🔐 Trace Secret k: {k_hex}...")
            return True, (TK_buf, k_buf)
        else:
            print("❌ Trace key generation failed - all zeros")
            return False, None
            
    except Exception as e:
        print(f"❌ Error in trace key generation test: {e}")
        return False, None

def test_address_generation(lib, keys, trace_keys):
    """Test address generation"""
    try:
        print("\n📧 Testing Address Generation...")
        
        A_buf, B_buf, a_buf, b_buf = keys
        TK_buf, k_buf = trace_keys
        
        buf_size = max(lib.stealth_element_size_G1(), lib.stealth_element_size_Zr(), 512)
        
        # Create output buffers
        addr_buf = create_string_buffer(buf_size)
        r1_buf = create_string_buffer(buf_size)
        r2_buf = create_string_buffer(buf_size)
        c_buf = create_string_buffer(buf_size)
        
        # Generate address
        lib.stealth_addr_gen_simple(
            A_buf.raw, B_buf.raw, TK_buf.raw,
            addr_buf, r1_buf, r2_buf, c_buf, buf_size
        )
        
        # Check if address was generated
        addr_hex = addr_buf.raw[:64].hex()
        r1_hex = r1_buf.raw[:64].hex()
        
        if addr_hex != "00" * 32 and r1_hex != "00" * 32:
            print("✅ Address generation successful")
            print(f"🏠 Address: {addr_hex}...")
            print(f"🎲 R1: {r1_hex}...")
            return True, (addr_buf, r1_buf, r2_buf, c_buf)
        else:
            print("❌ Address generation failed - all zeros")
            return False, None
            
    except Exception as e:
        print(f"❌ Error in address generation test: {e}")
        return False, None

def test_address_verification(lib, keys, address_data):
    """Test address verification"""
    try:
        print("\n🔍 Testing Address Verification...")
        
        A_buf, B_buf, a_buf, b_buf = keys
        addr_buf, r1_buf, r2_buf, c_buf = address_data
        
        # Verify address (fast version)
        result = lib.stealth_addr_verify_simple(
            r1_buf.raw, B_buf.raw, A_buf.raw, c_buf.raw, a_buf.raw
        )
        
        if result == 1:
            print("✅ Address verification successful")
            return True
        else:
            print("❌ Address verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in address verification test: {e}")
        return False

def test_performance(lib):
    """Test performance measurement"""
    try:
        print("\n📊 Testing Performance Measurement...")
        
        # Create results array
        results = (c_double * 7)()
        
        # Run performance test with 10 iterations (small for testing)
        lib.stealth_performance_test_simple(10, results)
        
        print("✅ Performance test completed")
        print(f"🏠 Address Generation: {results[0]:.3f} ms")
        print(f"🔍 Address Verification: {results[1]:.3f} ms")
        print(f"⚡ Fast Verification: {results[2]:.3f} ms")
        print(f"🔐 One-time SK Gen: {results[3]:.3f} ms")
        print(f"✍️ Signing: {results[4]:.3f} ms")
        print(f"✅ Signature Verification: {results[5]:.3f} ms")
        print(f"🔍 Identity Tracing: {results[6]:.3f} ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in performance test: {e}")
        return False

def main():
    print("🚀 Starting Enhanced Stealth Library Test")
    print("🏗️  Testing Separated Architecture (Core + Python API)")
    print("=" * 60)
    
    # Test 1: Load library
    lib = test_library_load()
    if not lib:
        sys.exit(1)
    
    # Test 2: Setup function signatures
    if not setup_function_signatures(lib):
        sys.exit(1)
    
    # Test 3: Initialize library
    if not test_initialization(lib):
        sys.exit(1)
    
    # Test 4: Key generation
    key_success, keys = test_key_generation(lib)
    if not key_success:
        sys.exit(1)
    
    # Test 5: Trace key generation
    trace_success, trace_keys = test_trace_key_generation(lib)
    if not trace_success:
        sys.exit(1)
    
    # Test 6: Address generation
    addr_success, address_data = test_address_generation(lib, keys, trace_keys)
    if not addr_success:
        sys.exit(1)
    
    # Test 7: Address verification
    if not test_address_verification(lib, keys, address_data):
        sys.exit(1)
    
    # Test 8: Performance measurement
    if not test_performance(lib):
        sys.exit(1)
    
    print("=" * 60)
    print("🎉 All tests passed! Separated architecture is working perfectly.")
    print("💡 You can now run the Flask app with the real C library:")
    print("   cd ../server && python3 app.py")
    
    # Cleanup
    try:
        lib.stealth_cleanup()
        print("🧹 Library cleanup completed")
    except:
        pass

if __name__ == "__main__":
    main()