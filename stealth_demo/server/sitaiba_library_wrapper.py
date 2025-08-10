"""
SITAIBA Library wrapper module.
Handles library loading, function signature setup, and low-level C function calls for SITAIBA scheme.
"""
from ctypes import *
from typing import Tuple


class SitaibaLibrary:
    """Wrapper class for the SITAIBA C library."""
    
    def __init__(self, library_path="../lib/libsitaiba.so"):
        # Try different paths to find the library
        import os
        possible_paths = [
            library_path,
            "../lib/libsitaiba.so", 
            "lib/libsitaiba.so",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib", "libsitaiba.so")
        ]
        
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                found_path = path
                break
        
        if found_path:
            library_path = found_path
        self.lib = None
        self.load_library(library_path)
        self.setup_function_signatures()
    
    def load_library(self, library_path: str):
        """Load the shared library."""
        try:
            self.lib = CDLL(library_path)
            print("✅ SITAIBA Library loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load SITAIBA library: {e}")
            raise
    
    def setup_function_signatures(self):
        """Setup all function signatures for the SITAIBA library."""
        # Core library management functions
        self.lib.sitaiba_init_simple.argtypes = [c_char_p]
        self.lib.sitaiba_init_simple.restype = c_int
        
        self.lib.sitaiba_is_initialized_simple.restype = c_int
        self.lib.sitaiba_cleanup_simple.restype = None
        self.lib.sitaiba_reset_performance_simple.restype = None
        
        self.lib.sitaiba_element_size_G1_simple.restype = c_int
        self.lib.sitaiba_element_size_Zr_simple.restype = c_int
        
        # Core cryptographic functions
        self.lib.sitaiba_keygen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.sitaiba_keygen_simple.restype = None
        
        self.lib.sitaiba_tracer_keygen_simple.argtypes = [c_char_p, c_char_p, c_int]
        self.lib.sitaiba_tracer_keygen_simple.restype = None
        
        self.lib.sitaiba_addr_gen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.sitaiba_addr_gen_simple.restype = None
        
        self.lib.sitaiba_addr_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        self.lib.sitaiba_addr_verify_simple.restype = c_int
        
        self.lib.sitaiba_addr_verify_fast_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        self.lib.sitaiba_addr_verify_fast_simple.restype = c_int
        
        self.lib.sitaiba_onetime_skgen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.sitaiba_onetime_skgen_simple.restype = None
        
        self.lib.sitaiba_trace_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.sitaiba_trace_simple.restype = None
        
        # Performance testing
        self.lib.sitaiba_performance_test_simple.argtypes = [c_int, POINTER(c_double)]
        self.lib.sitaiba_performance_test_simple.restype = None
        
        # Tracer key access
        self.lib.sitaiba_get_tracer_public_key_simple.argtypes = [c_char_p, c_int]
        self.lib.sitaiba_get_tracer_public_key_simple.restype = c_int
    
    def init(self, param_file_path: str) -> int:
        """Initialize the library with parameter file."""
        return self.lib.sitaiba_init_simple(param_file_path.encode())
    
    def is_initialized(self) -> bool:
        """Check if library is initialized."""
        return bool(self.lib.sitaiba_is_initialized_simple())
    
    def cleanup(self):
        """Cleanup library resources."""
        self.lib.sitaiba_cleanup_simple()
    
    def reset_performance(self):
        """Reset performance counters."""
        self.lib.sitaiba_reset_performance_simple()
    
    def get_element_sizes(self) -> Tuple[int, int]:
        """Get element sizes for G1 and Zr groups."""
        return self.lib.sitaiba_element_size_G1_simple(), self.lib.sitaiba_element_size_Zr_simple()
    
    def keygen(self, A_buf, B_buf, a_buf, b_buf, buf_size: int):
        """Generate user key pair."""
        self.lib.sitaiba_keygen_simple(A_buf, B_buf, a_buf, b_buf, buf_size)
    
    def tracer_keygen(self, A_m_buf, a_m_buf, buf_size: int):
        """Generate tracer key pair."""
        self.lib.sitaiba_tracer_keygen_simple(A_m_buf, a_m_buf, buf_size)
    
    def addr_gen(self, A_r_buf, B_r_buf, A_m_buf, addr_buf, r1_buf, r2_buf, buf_size: int):
        """Generate stealth address."""
        self.lib.sitaiba_addr_gen_simple(A_r_buf, B_r_buf, A_m_buf,
                                        addr_buf, r1_buf, r2_buf, buf_size)
    
    def addr_verify(self, addr_buf, r1_buf, r2_buf, A_r_buf, B_r_buf, a_r_buf, A_m_buf) -> bool:
        """Verify stealth address."""
        return bool(self.lib.sitaiba_addr_verify_simple(addr_buf, r1_buf, r2_buf, 
                                                        A_r_buf, B_r_buf, a_r_buf, A_m_buf))
    
    def addr_verify_fast(self, r1_buf, r2_buf, A_r_buf, a_r_buf) -> bool:
        """Fast verify stealth address."""
        return bool(self.lib.sitaiba_addr_verify_fast_simple(r1_buf, r2_buf, A_r_buf, a_r_buf))
    
    def onetime_skgen(self, r1_buf, a_r_buf, b_r_buf, A_m_buf, dsk_buf, buf_size: int):
        """Generate one-time secret key."""
        self.lib.sitaiba_onetime_skgen_simple(r1_buf, a_r_buf, b_r_buf, A_m_buf, dsk_buf, buf_size)
    
    def trace(self, addr_buf, r1_buf, r2_buf, a_m_buf, B_r_buf, buf_size: int):
        """Trace identity from stealth address."""
        self.lib.sitaiba_trace_simple(addr_buf, r1_buf, r2_buf, a_m_buf, B_r_buf, buf_size)
    
    def performance_test(self, iterations: int, results):
        """Run performance test."""
        self.lib.sitaiba_performance_test_simple(iterations, results)
    
    def get_tracer_public_key(self, A_m_buf, buf_size: int) -> int:
        """Get tracer public key."""
        return self.lib.sitaiba_get_tracer_public_key_simple(A_m_buf, buf_size)


# Global SITAIBA library instance
sitaiba_lib = SitaibaLibrary()