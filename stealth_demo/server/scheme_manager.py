"""
Multi-Scheme Manager for Stealth Demo
Handles dynamic loading and switching between different cryptographic schemes
"""

from ctypes import *
import os
import traceback
from typing import Dict, List, Optional, Any

class SchemeManager:
    """Manages multiple cryptographic schemes with dynamic library loading"""
    
    # Define available schemes and their properties
    SCHEMES = {
        'my_stealth': {
            'lib_name': 'libmy_stealth.so',
            'display_name': 'My Stealth Address',
            'description': 'Original traceable anonymous transaction scheme',
            'functions': ['init', 'keygen', 'tracekeygen', 'addr_gen', 'addr_verify', 'dsk_gen', 'sign', 'verify', 'trace', 'performance'],
            'param_type': 'pbc',
            'function_prefix': 'stealth_'
        },
        'cryptonote2': {
            'lib_name': 'libcryptonote2.so',
            'display_name': 'CryptoNote v2',
            'description': 'CryptoNote v2 protocol implementation',
            'functions': ['init', 'keygen', 'addr_gen', 'addr_verify', 'onetime_sk_gen', 'hash', 'performance'],
            'param_type': 'ecc',
            'function_prefix': 'cryptonote2_'
        },
        'zhao': {
            'lib_name': 'libzhao.so',
            'display_name': 'Zhao\'s Scheme',
            'description': 'Zhao et al. cryptographic scheme',
            'functions': ['init', 'keygen', 'sign', 'verify', 'hash', 'performance'],
            'param_type': 'ecc',
            'function_prefix': 'zhao_'
        },
        'hdwsa': {
            'lib_name': 'libhdwsa.so',
            'display_name': 'HDWSA',
            'description': 'Hierarchical Deterministic Wallet Signature Algorithm',
            'functions': ['init', 'keygen', 'sign', 'verify', 'master_keygen', 'derive_child', 'hash', 'performance'],
            'param_type': 'pbc',
            'function_prefix': 'hdwsa_'
        },
        'sitaiba': {
            'lib_name': 'libsitaiba.so',
            'display_name': 'Sitaiba\'s Scheme',
            'description': 'Sitaiba et al. cryptographic scheme',
            'functions': ['init', 'keygen', 'sign', 'verify', 'issue_credential', 'verify_credential', 'hash', 'performance'],
            'param_type': 'pbc',
            'function_prefix': 'sitaiba_'
        }
    }
    
    def __init__(self, lib_directory="../lib"):
        self.lib_directory = lib_directory
        self.current_scheme = None
        self.loaded_lib = None
        self.initialized = False
        
    def get_available_schemes(self) -> List[Dict[str, Any]]:
        """Get list of available schemes with their availability status"""
        available = []
        for scheme_id, scheme_info in self.SCHEMES.items():
            lib_path = os.path.join(self.lib_directory, scheme_info['lib_name'])
            is_available = os.path.exists(lib_path)
            
            available.append({
                'id': scheme_id,
                'name': scheme_info['display_name'],
                'description': scheme_info['description'],
                'functions': scheme_info['functions'],
                'param_type': scheme_info['param_type'],
                'available': is_available,
                'lib_path': lib_path if is_available else None
            })
        return available
    
    def switch_scheme(self, scheme_id: str) -> Dict[str, Any]:
        """Switch to a different cryptographic scheme"""
        if scheme_id not in self.SCHEMES:
            raise ValueError(f"Unknown scheme: {scheme_id}")
            
        scheme_info = self.SCHEMES[scheme_id]
        lib_path = os.path.join(self.lib_directory, scheme_info['lib_name'])
        
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Library not found: {lib_path}")
            
        try:
            # Cleanup previous library if needed
            if self.loaded_lib:
                self._cleanup_current_scheme()
            
            # Load new library
            self.loaded_lib = CDLL(lib_path)
            self.current_scheme = scheme_id
            self.initialized = False
            
            # Setup function signatures for the new scheme
            self._setup_function_signatures(scheme_info)
            
            return {
                'status': 'success',
                'scheme': scheme_id,
                'name': scheme_info['display_name'],
                'functions': scheme_info['functions'],
                'param_type': scheme_info['param_type']
            }
            
        except Exception as e:
            raise Exception(f"Failed to switch to scheme {scheme_id}: {str(e)}")
    
    def _cleanup_current_scheme(self):
        """Clean up current scheme resources"""
        try:
            if self.loaded_lib and self.initialized:
                # Try to call cleanup function if it exists
                prefix = self.SCHEMES[self.current_scheme]['function_prefix']
                cleanup_func_name = f"{prefix}cleanup"
                if hasattr(self.loaded_lib, cleanup_func_name):
                    cleanup_func = getattr(self.loaded_lib, cleanup_func_name)
                    cleanup_func()
        except:
            pass  # Ignore cleanup errors
        
        self.loaded_lib = None
        self.current_scheme = None
        self.initialized = False
    
    def _setup_function_signatures(self, scheme_info: Dict[str, Any]):
        """Setup function signatures for the loaded scheme based on its specific API"""
        prefix = scheme_info['function_prefix']
        scheme_id = self.current_scheme
        
        try:
            # Core management functions
            if 'init' in scheme_info['functions']:
                init_func = getattr(self.loaded_lib, f"{prefix}init")
                init_func.argtypes = [c_char_p]
                init_func.restype = c_int
                
                is_init_func = getattr(self.loaded_lib, f"{prefix}is_initialized", None)
                if is_init_func:
                    is_init_func.restype = c_int
                
                cleanup_func = getattr(self.loaded_lib, f"{prefix}cleanup", None)
                if cleanup_func:
                    cleanup_func.restype = None
            
            # Element size functions (for PBC-based schemes)
            if scheme_info['param_type'] == 'pbc':
                try:
                    g1_size_func = getattr(self.loaded_lib, f"{prefix}element_size_G1")
                    g1_size_func.restype = c_int
                    
                    zr_size_func = getattr(self.loaded_lib, f"{prefix}element_size_Zr") 
                    zr_size_func.restype = c_int
                except AttributeError:
                    pass  # Some schemes may not have these functions
            
            # Setup scheme-specific function signatures
            if scheme_id == 'my_stealth':
                self._setup_my_stealth_signatures(prefix)
            elif scheme_id == 'cryptonote2':
                self._setup_cryptonote2_signatures(prefix)
            elif scheme_id == 'zhao':
                self._setup_zhao_signatures(prefix)
            elif scheme_id == 'hdwsa':
                self._setup_hdwsa_signatures(prefix)
            elif scheme_id == 'sitaiba':
                self._setup_sitaiba_signatures(prefix)
            
            # Performance testing (common to all schemes)
            if 'performance' in scheme_info['functions']:
                perf_func = getattr(self.loaded_lib, f"{prefix}performance_test_simple")
                perf_func.argtypes = [c_int, POINTER(c_double)]
                perf_func.restype = None
                
        except AttributeError as e:
            raise Exception(f"Missing required function in scheme {self.current_scheme}: {str(e)}")
    
    def _setup_my_stealth_signatures(self, prefix: str):
        """Setup function signatures for my_stealth scheme"""
        # keygen(A_out, B_out, a_out, b_out, buf_size)
        keygen_func = getattr(self.loaded_lib, f"{prefix}keygen_simple")
        keygen_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        keygen_func.restype = None
        
        # tracekeygen(TK_out, k_out, buf_size)
        tracekeygen_func = getattr(self.loaded_lib, f"{prefix}tracekeygen_simple")
        tracekeygen_func.argtypes = [c_char_p, c_char_p, c_int]
        tracekeygen_func.restype = None
        
        # addr_gen(A_bytes, B_bytes, TK_bytes, addr_out, r1_out, r2_out, c_out, buf_size)
        addr_gen_func = getattr(self.loaded_lib, f"{prefix}addr_gen_simple")
        addr_gen_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        addr_gen_func.restype = None
        
        # addr_verify(R1_bytes, B_bytes, A_bytes, C_bytes, a_bytes)
        addr_verify_func = getattr(self.loaded_lib, f"{prefix}addr_verify_simple")
        addr_verify_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        addr_verify_func.restype = c_int
        
        # dsk_gen(addr_bytes, r1_bytes, a_bytes, b_bytes, dsk_out, buf_size)
        dsk_gen_func = getattr(self.loaded_lib, f"{prefix}dsk_gen_simple")
        dsk_gen_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        dsk_gen_func.restype = None
        
        # sign_with_dsk(addr_bytes, dsk_bytes, message, q_sigma_out, h_out, buf_size)
        sign_with_dsk_func = getattr(self.loaded_lib, f"{prefix}sign_with_dsk_simple")
        sign_with_dsk_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        sign_with_dsk_func.restype = None
        
        # sign(addr_bytes, r1_bytes, a_bytes, b_bytes, message, q_sigma_out, h_out, dsk_out, buf_size)
        sign_func = getattr(self.loaded_lib, f"{prefix}sign_simple")
        sign_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        sign_func.restype = None
        
        # verify(addr_bytes, r2_bytes, c_bytes, message, h_bytes, q_sigma_bytes)
        verify_func = getattr(self.loaded_lib, f"{prefix}verify_simple")
        verify_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
        verify_func.restype = c_int
        
        # trace(addr_bytes, r1_bytes, r2_bytes, c_bytes, k_bytes, b_recovered_out, buf_size)
        trace_func = getattr(self.loaded_lib, f"{prefix}trace_simple")
        trace_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        trace_func.restype = None
    
    def _setup_cryptonote2_signatures(self, prefix: str):
        """Setup function signatures for cryptonote2 scheme"""
        # keygen(A_out, B_out, a_out, b_out, buf_size)
        keygen_func = getattr(self.loaded_lib, f"{prefix}keygen_simple")
        keygen_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        keygen_func.restype = None
        
        # addr_gen(A_bytes, B_bytes, pk_one_out, r_out, buf_size)
        addr_gen_func = getattr(self.loaded_lib, f"{prefix}addr_gen_simple")
        addr_gen_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        addr_gen_func.restype = None
        
        # addr_verify(pk_one_bytes, r_bytes, a_bytes, b_bytes)
        addr_verify_func = getattr(self.loaded_lib, f"{prefix}addr_verify_simple")
        addr_verify_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        addr_verify_func.restype = c_int
        
        # onetime_sk_gen(r_bytes, a_bytes, b_bytes, sk_out, buf_size)
        onetime_sk_func = getattr(self.loaded_lib, f"{prefix}onetime_sk_gen_simple")
        onetime_sk_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        onetime_sk_func.restype = None
        
        # hash(point_bytes, hash_out, buf_size)
        hash_func = getattr(self.loaded_lib, f"{prefix}hash_simple")
        hash_func.argtypes = [c_char_p, c_char_p, c_int]
        hash_func.restype = None
        
        # hash_data(data, data_len, hash_out, buf_size)
        hash_data_func = getattr(self.loaded_lib, f"{prefix}hash_data_simple")
        hash_data_func.argtypes = [c_char_p, c_int, c_char_p, c_int]
        hash_data_func.restype = None
        
        # get_curve_info(curve_name, point_size, scalar_size, buffer_size)
        curve_info_func = getattr(self.loaded_lib, f"{prefix}get_curve_info")
        curve_info_func.argtypes = [c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
        curve_info_func.restype = None
    
    def _setup_zhao_signatures(self, prefix: str):
        """Setup function signatures for zhao scheme"""
        # keygen(public_key_out, private_key_out, buf_size)
        keygen_func = getattr(self.loaded_lib, f"{prefix}keygen_simple")
        keygen_func.argtypes = [c_char_p, c_char_p, c_int]
        keygen_func.restype = None
        
        # sign(message, private_key_bytes, signature_out, hash_out, buf_size)
        sign_func = getattr(self.loaded_lib, f"{prefix}sign_simple")
        sign_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        sign_func.restype = None
        
        # verify(message, public_key_bytes, signature_bytes, hash_bytes)
        verify_func = getattr(self.loaded_lib, f"{prefix}verify_simple")
        verify_func.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        verify_func.restype = c_int
        
        # hash(data, data_len, hash_out, buf_size)
        hash_func = getattr(self.loaded_lib, f"{prefix}hash_simple")
        hash_func.argtypes = [c_char_p, c_int, c_char_p, c_int]
        hash_func.restype = None
        
        # get_curve_info(curve_name, point_size, scalar_size, buffer_size)
        curve_info_func = getattr(self.loaded_lib, f"{prefix}get_curve_info")
        curve_info_func.argtypes = [c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
        curve_info_func.restype = None
    
    def _setup_hdwsa_signatures(self, prefix: str):
        """Setup function signatures for hdwsa scheme"""
        # keygen(public_key_out, private_key_out, buf_size)
        keygen_func = getattr(self.loaded_lib, f"{prefix}keygen_simple")
        keygen_func.argtypes = [c_char_p, c_char_p, c_int]
        keygen_func.restype = None
        
        # sign(message, private_key_bytes, signature_out, buf_size)
        sign_func = getattr(self.loaded_lib, f"{prefix}sign_simple")
        sign_func.argtypes = [c_char_p, c_char_p, c_char_p, c_int]
        sign_func.restype = None
        
        # verify(message, public_key_bytes, signature_bytes)
        verify_func = getattr(self.loaded_lib, f"{prefix}verify_simple")
        verify_func.argtypes = [c_char_p, c_char_p, c_char_p]
        verify_func.restype = c_int
        
        # master_keygen(seed, seed_len, master_secret_out, master_public_out, chain_code_out, buf_size)
        master_keygen_func = getattr(self.loaded_lib, f"{prefix}master_keygen_simple")
        master_keygen_func.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_int]
        master_keygen_func.restype = None
        
        # derive_child(parent_secret, parent_public, parent_chain, index, hardened, child_secret_out, child_public_out, child_chain_out, buf_size)
        derive_child_func = getattr(self.loaded_lib, f"{prefix}derive_child_simple")
        derive_child_func.argtypes = [c_char_p, c_char_p, c_char_p, c_uint, c_int, c_char_p, c_char_p, c_char_p, c_int]
        derive_child_func.restype = None
        
        # hash(data, data_len, hash_out, buf_size)
        hash_func = getattr(self.loaded_lib, f"{prefix}hash_simple")
        hash_func.argtypes = [c_char_p, c_int, c_char_p, c_int]
        hash_func.restype = None
    
    def _setup_sitaiba_signatures(self, prefix: str):
        """Setup function signatures for sitaiba scheme"""
        # keygen(public_key_out, private_key_out, buf_size)
        keygen_func = getattr(self.loaded_lib, f"{prefix}keygen_simple")
        keygen_func.argtypes = [c_char_p, c_char_p, c_int]
        keygen_func.restype = None
        
        # sign(message, private_key_bytes, signature_out, buf_size)
        sign_func = getattr(self.loaded_lib, f"{prefix}sign_simple")
        sign_func.argtypes = [c_char_p, c_char_p, c_char_p, c_int]
        sign_func.restype = None
        
        # verify(message, public_key_bytes, signature_bytes)
        verify_func = getattr(self.loaded_lib, f"{prefix}verify_simple")
        verify_func.argtypes = [c_char_p, c_char_p, c_char_p]
        verify_func.restype = c_int
        
        # issue_credential(identity, identity_len, issuer_key_bytes, credential_out, buf_size)
        issue_cred_func = getattr(self.loaded_lib, f"{prefix}issue_credential_simple")
        issue_cred_func.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_int]
        issue_cred_func.restype = None
        
        # verify_credential(credential_bytes, issuer_public_key_bytes, identity, identity_len)
        verify_cred_func = getattr(self.loaded_lib, f"{prefix}verify_credential_simple")
        verify_cred_func.argtypes = [c_char_p, c_char_p, c_char_p, c_int]
        verify_cred_func.restype = c_int
        
        # hash(data, data_len, hash_out, buf_size)
        hash_func = getattr(self.loaded_lib, f"{prefix}hash_simple")
        hash_func.argtypes = [c_char_p, c_int, c_char_p, c_int]
        hash_func.restype = None
    
    def get_current_scheme(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently loaded scheme"""
        if not self.current_scheme:
            return None
            
        scheme_info = self.SCHEMES[self.current_scheme]
        return {
            'id': self.current_scheme,
            'name': scheme_info['display_name'],
            'description': scheme_info['description'],
            'functions': scheme_info['functions'],
            'param_type': scheme_info['param_type'],
            'initialized': self.initialized
        }
    
    def get_lib(self):
        """Get the currently loaded library (for direct function calls)"""
        if not self.loaded_lib:
            raise Exception("No scheme loaded")
        return self.loaded_lib
    
    def is_function_available(self, function_name: str) -> bool:
        """Check if a function is available in the current scheme"""
        if not self.current_scheme:
            return False
        return function_name in self.SCHEMES[self.current_scheme]['functions']
    
    def get_function_prefix(self) -> str:
        """Get the function prefix for the current scheme"""
        if not self.current_scheme:
            raise Exception("No scheme loaded")
        return self.SCHEMES[self.current_scheme]['function_prefix']
    
    def mark_initialized(self):
        """Mark the current scheme as initialized"""
        self.initialized = True
    
    def is_initialized(self) -> bool:
        """Check if current scheme is initialized"""
        return self.initialized