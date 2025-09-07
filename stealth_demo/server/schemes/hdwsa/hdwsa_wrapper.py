"""
HDWSA C Library Python Wrapper

This module provides Python bindings for the HDWSA C library using ctypes.
It handles library loading, function signatures, and basic error handling.
"""

import ctypes
import os
from ctypes import c_int, c_char_p, c_void_p, POINTER


def _get_lib():
    """Load and return the HDWSA shared library."""
    lib_path = os.path.join(os.path.dirname(__file__), "../../../lib/libhdwsa.so")
    lib_path = os.path.abspath(lib_path)
    
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"HDWSA library not found at: {lib_path}")
    
    return ctypes.CDLL(lib_path)


# Global library instance
hdwsa_lib = None

def initialize_library():
    """Initialize the HDWSA library and setup function signatures."""
    global hdwsa_lib
    
    if hdwsa_lib is not None:
        return hdwsa_lib
    
    try:
        hdwsa_lib = _get_lib()
        
        # Setup function signatures
        _setup_function_signatures()
        
        return hdwsa_lib
        
    except Exception as e:
        raise Exception(f"Failed to initialize HDWSA library: {e}")


def _setup_function_signatures():
    """Setup ctypes function signatures for all HDWSA functions."""
    global hdwsa_lib
    
    # Library management functions
    hdwsa_lib.hdwsa_init_simple.argtypes = [c_char_p]
    hdwsa_lib.hdwsa_init_simple.restype = c_int
    
    hdwsa_lib.hdwsa_cleanup_simple.argtypes = []
    hdwsa_lib.hdwsa_cleanup_simple.restype = c_int
    
    # Element size functions
    hdwsa_lib.hdwsa_element_size_G1_simple.argtypes = []
    hdwsa_lib.hdwsa_element_size_G1_simple.restype = c_int
    
    hdwsa_lib.hdwsa_element_size_Zr_simple.argtypes = []
    hdwsa_lib.hdwsa_element_size_Zr_simple.restype = c_int
    
    hdwsa_lib.hdwsa_element_size_GT_simple.argtypes = []
    hdwsa_lib.hdwsa_element_size_GT_simple.restype = c_int
    
    # Key generation functions
    hdwsa_lib.hdwsa_root_keygen_simple.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]
    hdwsa_lib.hdwsa_root_keygen_simple.restype = c_int
    
    hdwsa_lib.hdwsa_keypair_gen_simple.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_char_p]
    hdwsa_lib.hdwsa_keypair_gen_simple.restype = c_int
    
    # Address functions
    hdwsa_lib.hdwsa_addr_gen_simple.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]
    hdwsa_lib.hdwsa_addr_gen_simple.restype = c_int
    
    hdwsa_lib.hdwsa_addr_recognize_simple.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p]
    hdwsa_lib.hdwsa_addr_recognize_simple.restype = c_int
    
    # DSK functions
    hdwsa_lib.hdwsa_dsk_gen_simple.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p]
    hdwsa_lib.hdwsa_dsk_gen_simple.restype = c_int
    
    # Signature functions
    hdwsa_lib.hdwsa_sign_simple.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_char_p]
    hdwsa_lib.hdwsa_sign_simple.restype = c_int
    
    hdwsa_lib.hdwsa_verify_simple.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_char_p]
    hdwsa_lib.hdwsa_verify_simple.restype = c_int
    
    # Performance functions
    hdwsa_lib.hdwsa_performance_test_simple.argtypes = [c_int]
    hdwsa_lib.hdwsa_performance_test_simple.restype = c_int
    
    hdwsa_lib.hdwsa_get_performance_string_simple.argtypes = [c_char_p, c_int]
    hdwsa_lib.hdwsa_get_performance_string_simple.restype = c_int
    
    hdwsa_lib.hdwsa_reset_performance_simple.argtypes = []
    hdwsa_lib.hdwsa_reset_performance_simple.restype = None


def get_library():
    """Get the initialized HDWSA library instance."""
    global hdwsa_lib
    
    if hdwsa_lib is None:
        initialize_library()
    
    return hdwsa_lib


def is_library_loaded():
    """Check if the HDWSA library is loaded and ready."""
    global hdwsa_lib
    return hdwsa_lib is not None


def cleanup_library():
    """Cleanup the HDWSA library resources."""
    global hdwsa_lib
    
    if hdwsa_lib is not None:
        try:
            hdwsa_lib.hdwsa_cleanup_simple()
        except:
            pass  # Ignore cleanup errors
        finally:
            hdwsa_lib = None