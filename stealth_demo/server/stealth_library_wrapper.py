"""
Stealth Library wrapper module.
Handles library loading, function signature setup, and low-level C function calls for Stealth scheme.
完全按照 debug_flask_app.py 的成功方法重寫
"""
from ctypes import *
from typing import Tuple


class StealthLibrary:
    """Wrapper class for the Stealth C library."""
    
    def __init__(self, library_path="../lib/libstealth.so"):
        # Try different paths to find the library
        import os
        possible_paths = [
            library_path,
            "../lib/libstealth.so", 
            "lib/libstealth.so",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib", "libstealth.so")
        ]
        
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                found_path = path
                break
        
        if found_path:
            library_path = found_path
        self.lib = None
        self.g1_size = 0
        self.zr_size = 0
        self.load_library(library_path)
        self.setup_function_signatures()
    
    def load_library(self, library_path: str):
        """Load the shared library."""
        try:
            self.lib = CDLL(library_path)
            print("✅ Stealth Library loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Stealth library: {e}")
            raise
    
    def setup_function_signatures(self):
        """Setup all function signatures exactly like debug_flask_app.py"""
        # Core library management functions
        self.lib.stealth_init.argtypes = [c_char_p]
        self.lib.stealth_init.restype = c_int
        
        self.lib.stealth_is_initialized.restype = c_int
        self.lib.stealth_cleanup.restype = None
        self.lib.stealth_reset_performance.restype = None
        
        # Element size functions
        self.lib.stealth_element_size_G1.restype = c_int
        self.lib.stealth_element_size_Zr.restype = c_int
        
        # Key generation functions
        self.lib.stealth_keygen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_keygen_simple.restype = None
        
        self.lib.stealth_tracekeygen_simple.argtypes = [c_char_p, c_char_p, c_int]
        self.lib.stealth_tracekeygen_simple.restype = None
        
        # Address generation and verification
        self.lib.stealth_addr_gen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_addr_gen_simple.restype = None
        
        self.lib.stealth_addr_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        self.lib.stealth_addr_verify_simple.restype = c_int
        
        # Signing functions  
        self.lib.stealth_sign_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_sign_simple.restype = None
        
        # Verification function
        self.lib.stealth_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        self.lib.stealth_verify_simple.restype = c_int
        
        # Tracing function
        self.lib.stealth_trace_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        self.lib.stealth_trace_simple.restype = None
        
        # Performance test
        self.lib.stealth_performance_test_simple.argtypes = [c_int, POINTER(c_double)]
        self.lib.stealth_performance_test_simple.restype = None
    
    def init(self, param_file: str) -> bool:
        """Initialize the library with parameter file."""
        result = self.lib.stealth_init(param_file.encode('utf-8'))
        success = (result == 0)
        if success:
            self.g1_size = self.lib.stealth_element_size_G1()
            self.zr_size = self.lib.stealth_element_size_Zr()
        return success
    
    def is_initialized(self) -> bool:
        """Check if library is initialized."""
        return self.lib.stealth_is_initialized() == 1
    
    def cleanup(self):
        """Cleanup library resources."""
        if self.lib:
            self.lib.stealth_cleanup()
    
    def reset_performance(self):
        """Reset performance counters."""
        if self.lib:
            self.lib.stealth_reset_performance()
    
    def get_element_size_G1(self) -> int:
        """Get size needed for G1 element serialization."""
        return self.g1_size if self.g1_size > 0 else self.lib.stealth_element_size_G1()
    
    def get_element_size_Zr(self) -> int:
        """Get size needed for Zr element serialization."""
        return self.zr_size if self.zr_size > 0 else self.lib.stealth_element_size_Zr()
    
    def get_fixed_hex(self, buf, element_type):
        """獲取固定大小的 hex 數據 - 按照 debug_flask_app.py"""
        if element_type == 'G1':
            size = self.get_element_size_G1()
        elif element_type == 'Zr':
            size = self.get_element_size_Zr()
        else:
            raise ValueError(f"未知元素類型: {element_type}")
        
        if size > len(buf.raw):
            size = len(buf.raw)
        
        data = buf.raw[:size]
        return data
    
    def keygen(self, buf_size: int) -> Tuple[bytes, bytes, bytes, bytes]:
        """Generate key pair (A, B, a, b) - 完全按照 debug_flask_app.py"""
        buf_size = max(self.get_element_size_G1(), self.get_element_size_Zr(), buf_size)
        
        A_buf = create_string_buffer(buf_size)
        B_buf = create_string_buffer(buf_size)
        a_buf = create_string_buffer(buf_size)
        b_buf = create_string_buffer(buf_size)
        
        # 清零
        for buf in [A_buf, B_buf, a_buf, b_buf]:
            for i in range(buf_size):
                buf[i] = 0
        
        self.lib.stealth_keygen_simple(A_buf, B_buf, a_buf, b_buf, buf_size)
        
        A_bytes = self.get_fixed_hex(A_buf, 'G1')
        B_bytes = self.get_fixed_hex(B_buf, 'G1')
        a_bytes = self.get_fixed_hex(a_buf, 'Zr')
        b_bytes = self.get_fixed_hex(b_buf, 'Zr')
        
        return (A_bytes, B_bytes, a_bytes, b_bytes)
    
    def tracekeygen(self, buf_size: int) -> Tuple[bytes, bytes]:
        """Generate trace key pair (TK, k) - 完全按照 debug_flask_app.py"""
        buf_size = max(self.get_element_size_G1(), self.get_element_size_Zr(), buf_size)
        
        TK_buf = create_string_buffer(buf_size)
        k_buf = create_string_buffer(buf_size)
        
        for i in range(buf_size):
            TK_buf[i] = 0
            k_buf[i] = 0
        
        self.lib.stealth_tracekeygen_simple(TK_buf, k_buf, buf_size)
        
        TK_bytes = self.get_fixed_hex(TK_buf, 'G1')
        k_bytes = self.get_fixed_hex(k_buf, 'Zr')
        
        return (TK_bytes, k_bytes)
    
    def addr_gen(self, A: bytes, B: bytes, TK: bytes, buf_size: int) -> Tuple[bytes, bytes, bytes, bytes]:
        """Generate stealth address - 完全按照 debug_flask_app.py"""
        buf_size = max(self.get_element_size_G1(), self.get_element_size_Zr(), buf_size)
        
        addr_buf = create_string_buffer(buf_size)
        r1_buf = create_string_buffer(buf_size)
        r2_buf = create_string_buffer(buf_size)
        c_buf = create_string_buffer(buf_size)
        
        for buf in [addr_buf, r1_buf, r2_buf, c_buf]:
            for i in range(buf_size):
                buf[i] = 0
        
        self.lib.stealth_addr_gen_simple(A, B, TK,
                                        addr_buf, r1_buf, r2_buf, c_buf, buf_size)
        
        addr_bytes = self.get_fixed_hex(addr_buf, 'G1')
        r1_bytes = self.get_fixed_hex(r1_buf, 'G1')
        r2_bytes = self.get_fixed_hex(r2_buf, 'G1')
        c_bytes = self.get_fixed_hex(c_buf, 'G1')
        
        return (addr_bytes, r1_bytes, r2_bytes, c_bytes)
    
    def addr_verify(self, R1: bytes, B: bytes, A: bytes, C: bytes, a: bytes) -> bool:
        """Verify stealth address - 完全按照 debug_flask_app.py"""
        result = self.lib.stealth_addr_verify_simple(R1, B, A, C, a)
        return result == 1
    
    def dsk_gen(self, addr: bytes, r1: bytes, a: bytes, b: bytes, buf_size: int) -> bytes:
        """Generate one-time secret key (DSK) - 用於兼容性，實際不在 debug_flask_app.py 中"""
        raise NotImplementedError("DSK generation not implemented in debug_flask_app.py style")
    
    def sign(self, addr: bytes, r1: bytes, a: bytes, b: bytes, message: str, buf_size: int) -> Tuple[bytes, bytes, bytes]:
        """Sign message - 完全按照 debug_flask_app.py"""
        message_bytes = message.encode('utf-8')
        buf_size = max(self.get_element_size_G1(), self.get_element_size_Zr(), buf_size)
        
        q_sigma_buf = create_string_buffer(buf_size)
        h_buf = create_string_buffer(buf_size)
        dsk_buf = create_string_buffer(buf_size)
        
        for buf in [q_sigma_buf, h_buf, dsk_buf]:
            for i in range(buf_size):
                buf[i] = 0
        
        self.lib.stealth_sign_simple(addr, r1, a, b, message_bytes,
                                    q_sigma_buf, h_buf, dsk_buf, buf_size)
        
        q_sigma_bytes = self.get_fixed_hex(q_sigma_buf, 'G1')
        h_bytes = self.get_fixed_hex(h_buf, 'Zr')
        dsk_bytes = self.get_fixed_hex(dsk_buf, 'G1')  # DSK 在 debug_flask_app.py 中被視為 G1
        
        return (q_sigma_bytes, h_bytes, dsk_bytes)
    
    def sign_with_dsk(self, addr: bytes, dsk: bytes, message: str, buf_size: int) -> Tuple[bytes, bytes]:
        """Sign message with existing DSK - 用於兼容性，但不在 debug_flask_app.py 中"""
        raise NotImplementedError("sign_with_dsk not implemented in debug_flask_app.py style")
    
    def verify(self, addr: bytes, r2: bytes, c: bytes, message: str, h: bytes, q_sigma: bytes) -> bool:
        """Verify signature - 完全按照 debug_flask_app.py"""
        message_bytes = message.encode('utf-8')
        
        verify_result = self.lib.stealth_verify_simple(addr, r2, c, message_bytes, h, q_sigma)
        
        return verify_result == 1
    
    def trace(self, addr: bytes, r1: bytes, r2: bytes, c: bytes, k: bytes, buf_size: int) -> bytes:
        """Trace identity - 完全按照 debug_flask_app.py"""
        buf_size = max(self.get_element_size_G1(), self.get_element_size_Zr(), buf_size)
        
        recovered_b_buf = create_string_buffer(buf_size)
        
        for i in range(buf_size):
            recovered_b_buf[i] = 0
        
        self.lib.stealth_trace_simple(addr, r1, r2, c, k,
                                     recovered_b_buf, buf_size)
        
        recovered_b_bytes = self.get_fixed_hex(recovered_b_buf, 'G1')
        
        return recovered_b_bytes
    
    def performance_test(self, iterations: int) -> dict:
        """Run performance test and return results."""
        results = (c_double * 7)()
        
        self.lib.stealth_performance_test_simple(iterations, results)
        
        return {
            'addr_gen_avg': results[0],
            'addr_verify_avg': results[1], 
            'fast_verify_avg': results[2],
            'onetime_sk_avg': results[3],
            'sign_avg': results[4],
            'verify_avg': results[5],
            'trace_avg': results[6]
        }


# Global library instance
stealth_lib = None

def get_stealth_library() -> StealthLibrary:
    """Get global stealth library instance."""
    global stealth_lib
    if stealth_lib is None:
        stealth_lib = StealthLibrary()
    return stealth_lib