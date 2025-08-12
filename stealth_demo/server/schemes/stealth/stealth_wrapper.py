"""
C Library wrapper module for stealth cryptographic operations.
Handles library loading, function signature setup, and low-level C function calls.
"""
from ctypes import *
from typing import Tuple


class StealthLibrary:
    """Wrapper class for the stealth C library."""
    
    def __init__(self, library_path="/mnt/c/Users/chen1/Desktop/master/thesis/nccu/new/code/stealth_demo/lib/libstealth.so"):
        self.lib = None
        self.dsk_functions_available = False
        self.load_library(library_path)
        self.setup_function_signatures()
    
    def load_library(self, library_path: str):
        """Load the shared library."""
        try:
            self.lib = CDLL(library_path)
            print("✅ Library loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load library: {e}")
            raise
    
    def setup_function_signatures(self):
        """Setup all function signatures for the library."""
        # Core library management functions
        self.lib.stealth_init.argtypes = [c_char_p]
        self.lib.stealth_init.restype = c_int
        
        self.lib.stealth_is_initialized.restype = c_int
        self.lib.stealth_cleanup.restype = None
        self.lib.stealth_reset_performance.restype = None
        
        self.lib.stealth_element_size_G1.restype = c_int
        self.lib.stealth_element_size_Zr.restype = c_int
        
        self.lib.stealth_get_pairing.restype = c_void_p
        
        # Existing Python interface functions
        self.lib.stealth_keygen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_keygen_simple.restype = None
        
        self.lib.stealth_tracekeygen_simple.argtypes = [c_char_p, c_char_p, c_int]
        self.lib.stealth_tracekeygen_simple.restype = None
        
        self.lib.stealth_addr_gen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_addr_gen_simple.restype = None
        
        # Fast address recognition function
        self.lib.stealth_addr_recognize_fast_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        self.lib.stealth_addr_recognize_fast_simple.restype = c_int
        
        # Full address recognition function
        self.lib.stealth_addr_recognize_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        self.lib.stealth_addr_recognize_simple.restype = c_int
        
        self.lib.stealth_sign_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_sign_simple.restype = None
        
        self.lib.stealth_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        self.lib.stealth_verify_simple.restype = c_int
        
        self.lib.stealth_trace_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_trace_simple.restype = None
        
        # Performance testing
        self.lib.stealth_performance_test_simple.argtypes = [c_int, POINTER(c_double)]
        self.lib.stealth_performance_test_simple.restype = None
        
        # Try to load DSK functions
        self._setup_dsk_functions()
    
    def _setup_dsk_functions(self):
        """Try to setup DSK functions (new functionality)."""
        try:
            self.lib.stealth_dsk_gen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
            self.lib.stealth_dsk_gen_simple.restype = None
            
            self.lib.stealth_sign_with_dsk_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
            self.lib.stealth_sign_with_dsk_simple.restype = None
            
            print("✅ New DSK functions loaded")
            self.dsk_functions_available = True
        except AttributeError:
            print("⚠️ DSK functions not available - using fallback implementation")
            self.dsk_functions_available = False
    
    def init(self, param_file_path: str) -> int:
        """Initialize the library with parameter file."""
        return self.lib.stealth_init(param_file_path.encode())
    
    def is_initialized(self) -> bool:
        """Check if library is initialized."""
        return bool(self.lib.stealth_is_initialized())
    
    def cleanup(self):
        """Cleanup library resources."""
        self.lib.stealth_cleanup()
    
    def reset_performance(self):
        """Reset performance counters."""
        self.lib.stealth_reset_performance()
    
    def get_element_sizes(self) -> Tuple[int, int]:
        """Get element sizes for G1 and Zr groups."""
        return self.lib.stealth_element_size_G1(), self.lib.stealth_element_size_Zr()
    
    def keygen(self, A_buf, B_buf, a_buf, b_buf, buf_size: int):
        """Generate key pair."""
        self.lib.stealth_keygen_simple(A_buf, B_buf, a_buf, b_buf, buf_size)
    
    def tracekeygen(self, TK_buf, k_buf, buf_size: int):
        """Generate trace key."""
        self.lib.stealth_tracekeygen_simple(TK_buf, k_buf, buf_size)
    
    def addr_gen(self, A_bytes, B_bytes, TK_bytes, addr_buf, r1_buf, r2_buf, c_buf, buf_size: int):
        """Generate stealth address."""
        self.lib.stealth_addr_gen_simple(A_bytes, B_bytes, TK_bytes,
                                        addr_buf, r1_buf, r2_buf, c_buf, buf_size)
    
    def addr_recognize_fast(self, r1_bytes, b_bytes, a_bytes, c_bytes, a_priv_bytes) -> bool:
        """Recognize stealth address (fast version)."""
        return bool(self.lib.stealth_addr_recognize_fast_simple(r1_bytes, b_bytes, a_bytes, c_bytes, a_priv_bytes))
    
    def addr_recognize(self, addr_bytes, r1_bytes, b_bytes, a_bytes, c_bytes, a_priv_bytes, tk_bytes) -> bool:
        """Recognize stealth address (full version)."""
        return bool(self.lib.stealth_addr_recognize_simple(addr_bytes, r1_bytes, b_bytes, a_bytes, c_bytes, a_priv_bytes, tk_bytes))
    
    def sign(self, addr_bytes, r1_bytes, a_bytes, b_bytes, message_bytes, 
             q_sigma_buf, h_buf, dsk_buf, buf_size: int):
        """Sign message with stealth address."""
        self.lib.stealth_sign_simple(addr_bytes, r1_bytes, a_bytes, b_bytes, message_bytes,
                                    q_sigma_buf, h_buf, dsk_buf, buf_size)
    
    def verify(self, addr_bytes, r2_bytes, c_bytes, message_bytes, h_bytes, q_sigma_bytes) -> bool:
        """Verify signature."""
        return bool(self.lib.stealth_verify_simple(addr_bytes, r2_bytes, c_bytes, 
                                                  message_bytes, h_bytes, q_sigma_bytes))
    
    def trace(self, addr_bytes, r1_bytes, r2_bytes, c_bytes, k_bytes, b_recovered_buf, buf_size: int):
        """Trace identity from stealth address."""
        self.lib.stealth_trace_simple(addr_bytes, r1_bytes, r2_bytes, c_bytes, k_bytes,
                                     b_recovered_buf, buf_size)
    
    def dsk_gen(self, addr_bytes, r1_bytes, a_bytes, b_bytes, dsk_buf, buf_size: int):
        """Generate DSK (if available)."""
        if self.dsk_functions_available:
            self.lib.stealth_dsk_gen_simple(addr_bytes, r1_bytes, a_bytes, b_bytes, dsk_buf, buf_size)
        else:
            raise NotImplementedError("DSK functions not available")
    
    def sign_with_dsk(self, addr_bytes, dsk_bytes, message_bytes, q_sigma_buf, h_buf, buf_size: int):
        """Sign with DSK (if available)."""
        if self.dsk_functions_available:
            self.lib.stealth_sign_with_dsk_simple(addr_bytes, dsk_bytes, message_bytes,
                                                 q_sigma_buf, h_buf, buf_size)
        else:
            raise NotImplementedError("DSK functions not available")
    
    def performance_test(self, iterations: int, results):
        """Run performance test."""
        self.lib.stealth_performance_test_simple(iterations, results)


# Global library instance - lazy initialization
stealth_lib = None

def get_stealth_lib():
    """Get the global stealth library instance, initializing if needed."""
    global stealth_lib
    if stealth_lib is None:
        stealth_lib = StealthLibrary()
    return stealth_lib