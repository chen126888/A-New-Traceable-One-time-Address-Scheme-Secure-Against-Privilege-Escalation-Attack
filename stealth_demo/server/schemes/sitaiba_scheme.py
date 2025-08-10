"""
SITAIBA Scheme implementation.
Wraps the SITAIBA cryptographic operations into the plugin architecture.
SITAIBA: SIgnature-based TrAceable anonymIty using BilineAr mapping
"""
from typing import Dict, List, Any, Optional
from .base_scheme import BaseScheme, SchemeInfo
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sitaiba_library_wrapper import sitaiba_lib
from sitaiba_utils import (
    get_sitaiba_element_size, create_sitaiba_buffer, create_multiple_sitaiba_buffers,
    bytes_to_hex_safe_fixed_sitaiba, hex_to_bytes_safe_sitaiba, 
    validate_sitaiba_index, find_matching_sitaiba_key
)


class SitaibaScheme(BaseScheme):
    """Implementation of the SITAIBA cryptographic scheme."""
    
    def __init__(self, scheme_info: SchemeInfo = None):
        if scheme_info is None:
            scheme_info = SchemeInfo(
                name="sitaiba",
                version="1.0.0", 
                description="",
                capabilities=[
                    'setup', 'keygen', 'addrgen', 'verify_addr', 'fast_verify', 
                    'dskgen', 'trace', 'performance'
                ],
                param_files=[
                    'a.param', 'a1.param', 'd105171-196-185.param', 'd159.param',
                    'd201.param', 'd224.param', 'd277699-175-167.param', 
                    'd278027-190-181.param', 'e.param', 'f.param', 'g149.param', 'i.param'
                ],
                author="Chen et al."
            )
        super().__init__(scheme_info)
        
        # SITAIBA-specific storage
        self._keys: List[Dict] = []
        self._addresses: List[Dict] = []  
        self._dsks: List[Dict] = []
        self._tracer_key: Optional[Dict] = None
        
        # Store reference to SITAIBA library
        self._library = sitaiba_lib
    
    def get_info(self) -> SchemeInfo:
        """Get scheme information."""
        return self.info
    
    def setup_system(self, param_file: str) -> Dict[str, Any]:
        """Initialize the SITAIBA scheme with parameter file."""
        if not self.validate_param_file(param_file):
            raise ValueError(f"Parameter file {param_file} not supported by SITAIBA scheme")
        
        full_path = f"../param/pbc/{param_file}"
        
        print(f"🔧 Initializing SITAIBA with {full_path}")
        result = self._library.init(full_path)
        
        if result != 0:
            raise Exception(f"SITAIBA library initialization failed with code: {result}")
        
        if not self._library.is_initialized():
            raise Exception("SITAIBA library initialization verification failed")
        
        self.initialized = True
        self.current_param_file = param_file
        
        # Get tracer key (automatically generated during init)
        tracer_key = self._generate_tracer_key_info()
        self._tracer_key = tracer_key
        
        # Clear existing data
        self._keys.clear()
        self._addresses.clear() 
        self._dsks.clear()
        
        g1_size, zr_size = self._library.get_element_sizes()
        
        return {
            "status": "setup complete",
            "message": f"SITAIBA scheme initialized with {param_file}",
            "param_file": param_file,
            "scheme_name": self.info.name,
            "scheme_version": self.info.version,
            "g1_size": g1_size,
            "zr_size": zr_size,
            "tracer_key_available": self._tracer_key is not None,
            **tracer_key
        }
    
    def reset_system(self) -> Dict[str, Any]:
        """Reset the SITAIBA scheme state."""
        if self.initialized:
            self._library.reset_performance()
        
        self._keys.clear()
        self._addresses.clear()
        self._dsks.clear() 
        self._tracer_key = None
        self.initialized = False
        self.current_param_file = None
        
        return {
            "status": "reset complete",
            "message": "SITAIBA scheme state has been reset",
            "scheme_name": self.info.name,
            "keys_count": 0,
            "addresses_count": 0
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current SITAIBA scheme status."""
        status = {
            "initialized": self.initialized,
            "param_file": self.current_param_file,
            "scheme_name": self.info.name,
            "scheme_version": self.info.version,
            "capabilities": self.info.capabilities,
            "keys_count": len(self._keys),
            "addresses_count": len(self._addresses),
            "dsks_count": len(self._dsks),
            "tracer_key_set": self._tracer_key is not None,
            "architecture": "no_signing_scheme"
        }
        
        # Add library-specific information
        try:
            if self.initialized:
                g1_size, zr_size = self._library.get_element_sizes()
                status.update({
                    "g1_element_size": g1_size,
                    "zr_element_size": zr_size
                })
        except:
            pass
        
        status["library_loaded"] = True
        return status
    
    def _generate_tracer_key_info(self) -> Dict[str, Any]:
        """Generate tracer key information from initialized library."""
        buf_size = get_sitaiba_element_size()
        A_m_buf = create_sitaiba_buffer(buf_size)
        
        # Get tracer public key from library
        result = self._library.get_tracer_public_key(A_m_buf, buf_size)
        if result != 0:
            raise Exception("Failed to get tracer public key")
        
        A_m_hex = bytes_to_hex_safe_fixed_sitaiba(A_m_buf, 'G1')
        
        if not A_m_hex:
            raise Exception("Failed to get tracer public key hex")
        
        return {
            "tracer_A_hex": A_m_hex,
            "tracer_key_status": "available",
            "tracer_key_note": "Private key secured in C library"
        }
    
    def generate_keypair(self, **kwargs) -> Dict[str, Any]:
        """Generate a SITAIBA user key pair."""
        if not self.initialized:
            raise RuntimeError("SITAIBA scheme not initialized")
        
        buf_size = get_sitaiba_element_size()
        A_buf, B_buf, a_buf, b_buf = create_multiple_sitaiba_buffers(4, buf_size)
        
        self._library.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)
        
        A_hex = bytes_to_hex_safe_fixed_sitaiba(A_buf, 'G1')
        B_hex = bytes_to_hex_safe_fixed_sitaiba(B_buf, 'G1')
        a_hex = bytes_to_hex_safe_fixed_sitaiba(a_buf, 'Zr')
        b_hex = bytes_to_hex_safe_fixed_sitaiba(b_buf, 'Zr')
        
        if not all([A_hex, B_hex, a_hex, b_hex]):
            raise Exception("Failed to generate SITAIBA key pair")
        
        item = {
            "index": len(self._keys),
            "id": f"sitaiba_key_{len(self._keys)}",
            "A_hex": A_hex,
            "B_hex": B_hex,
            "a_hex": a_hex,
            "b_hex": b_hex,
            "param_file": self.current_param_file,
            "scheme": "sitaiba",
            "status": "generated"
        }
        
        self._keys.append(item)
        return item
    
    def generate_address(self, key_index: int, **kwargs) -> Dict[str, Any]:
        """Generate SITAIBA stealth address."""
        if not self.initialized:
            raise RuntimeError("SITAIBA scheme not initialized")
        
        validate_sitaiba_index(key_index, self._keys, "key_index")
        
        if not self._tracer_key:
            raise Exception("Tracer key not available")
        
        selected_key = self._keys[key_index]
        
        # Use the stored key data (convert hex back to bytes)
        A_bytes = hex_to_bytes_safe_sitaiba(selected_key['A_hex'])
        B_bytes = hex_to_bytes_safe_sitaiba(selected_key['B_hex'])
        a_bytes = hex_to_bytes_safe_sitaiba(selected_key['a_hex'])
        
        buf_size = get_sitaiba_element_size()
        
        addr_buf, r1_buf, r2_buf = create_multiple_sitaiba_buffers(3, buf_size)
        
        # Use None for A_m_buf to use internal tracer key
        self._library.addr_gen(A_bytes, B_bytes, None, addr_buf, r1_buf, r2_buf, buf_size)
        
        addr_hex = bytes_to_hex_safe_fixed_sitaiba(addr_buf, 'G1')
        r1_hex = bytes_to_hex_safe_fixed_sitaiba(r1_buf, 'G1')
        r2_hex = bytes_to_hex_safe_fixed_sitaiba(r2_buf, 'G1')
        
        if not all([addr_hex, r1_hex, r2_hex]):
            raise Exception("Failed to generate SITAIBA address")
        
        address_item = {
            "index": len(self._addresses),
            "id": f"sitaiba_addr_{len(self._addresses)}",
            "addr_hex": addr_hex,
            "r1_hex": r1_hex,
            "r2_hex": r2_hex,
            "key_index": key_index,
            "key_id": selected_key['id'],
            "owner_A": selected_key['A_hex'], 
            "owner_B": selected_key['B_hex'],
            "tracer_A": self._tracer_key['tracer_A_hex'],
            "scheme": "sitaiba",
            "status": "generated"
        }
        
        self._addresses.append(address_item)
        return address_item
    
    def verify_address(self, address_index: int, key_index: int, **kwargs) -> Dict[str, Any]:
        """Verify SITAIBA stealth address."""
        if not self.initialized:
            raise RuntimeError("SITAIBA scheme not initialized")
        
        validate_sitaiba_index(address_index, self._addresses, "address_index")
        validate_sitaiba_index(key_index, self._keys, "key_index")
        
        address_data = self._addresses[address_index]
        key_data = self._keys[key_index]
        
        addr_bytes = hex_to_bytes_safe_sitaiba(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe_sitaiba(address_data['r1_hex'])
        r2_bytes = hex_to_bytes_safe_sitaiba(address_data['r2_hex'])
        A_bytes = hex_to_bytes_safe_sitaiba(key_data['A_hex'])
        B_bytes = hex_to_bytes_safe_sitaiba(key_data['B_hex'])
        a_bytes = hex_to_bytes_safe_sitaiba(key_data['a_hex'])
        
        # Use None for A_m_buf to use internal tracer key
        result = self._library.addr_verify(addr_bytes, r1_bytes, r2_bytes, 
                                          A_bytes, B_bytes, a_bytes, None)
        
        return {
            "valid": result,
            "address_index": address_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "is_owner": (address_data['key_index'] == key_index),
            "verification_method": "sitaiba_full",
            "status": "valid" if result else "invalid"
        }
    
    def generate_dsk(self, address_index: int, key_index: int, **kwargs) -> Dict[str, Any]:
        """Generate one-time secret key for SITAIBA."""
        if not self.initialized:
            raise RuntimeError("SITAIBA scheme not initialized")
        
        validate_sitaiba_index(address_index, self._addresses, "address_index")
        validate_sitaiba_index(key_index, self._keys, "key_index")
        
        address_data = self._addresses[address_index]
        key_data = self._keys[key_index]
        
        r1_bytes = hex_to_bytes_safe_sitaiba(address_data['r1_hex'])
        a_bytes = hex_to_bytes_safe_sitaiba(key_data['a_hex'])
        b_bytes = hex_to_bytes_safe_sitaiba(key_data['b_hex'])
        
        buf_size = get_sitaiba_element_size()
        dsk_buf = create_sitaiba_buffer(buf_size)
        
        # Use None for A_m_buf to use internal tracer key
        self._library.onetime_skgen(r1_bytes, a_bytes, b_bytes, None, dsk_buf, buf_size)
        
        dsk_hex = bytes_to_hex_safe_fixed_sitaiba(dsk_buf, 'Zr')
        
        if not dsk_hex:
            raise Exception("Failed to generate SITAIBA DSK")
        
        dsk_item = {
            "index": len(self._dsks),
            "id": f"sitaiba_dsk_{len(self._dsks)}",
            "dsk_hex": dsk_hex,
            "address_index": address_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "owner_A": key_data['A_hex'],
            "owner_B": key_data['B_hex'],
            "for_address": address_data['addr_hex'],
            "scheme": "sitaiba",
            "method": "sitaiba_onetime_sk",
            "status": "generated"
        }
        
        self._dsks.append(dsk_item)
        return dsk_item
    
    def trace_identity(self, address_index: int, **kwargs) -> Dict[str, Any]:
        """Trace identity for SITAIBA address."""
        if not self.initialized:
            raise RuntimeError("SITAIBA scheme not initialized")
        
        validate_sitaiba_index(address_index, self._addresses, "address_index")
        
        address_data = self._addresses[address_index]
        
        addr_bytes = hex_to_bytes_safe_sitaiba(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe_sitaiba(address_data['r1_hex'])
        r2_bytes = hex_to_bytes_safe_sitaiba(address_data['r2_hex'])
        
        buf_size = get_sitaiba_element_size()
        b_recovered_buf = create_sitaiba_buffer(buf_size)
        
        # Use None for a_m_buf to use internal tracer private key
        self._library.trace(addr_bytes, r1_bytes, r2_bytes, None, b_recovered_buf, buf_size)
        
        b_recovered_hex = bytes_to_hex_safe_fixed_sitaiba(b_recovered_buf, 'G1')
        
        if not b_recovered_hex:
            raise Exception("Failed to trace SITAIBA identity")
        
        # Find matching key
        matched_key = find_matching_sitaiba_key(b_recovered_hex, self._keys)
        
        return {
            "recovered_b_hex": b_recovered_hex,
            "address_index": address_index,
            "address_id": address_data['id'],
            "original_owner": {
                "key_index": address_data['key_index'],
                "key_id": address_data['key_id'],
                "B_hex": address_data['owner_B']
            },
            "matched_key": matched_key,
            "perfect_match": matched_key is not None,
            "scheme": "sitaiba",
            "status": "traced"
        }
    
    def performance_test(self, iterations: int = 100, **kwargs) -> Dict[str, Any]:
        """Run SITAIBA scheme performance test."""
        if not self.initialized:
            raise RuntimeError("SITAIBA scheme not initialized")
        
        iterations = min(iterations, 1000)  # Limit iterations
        
        print(f"🧪 Running SITAIBA performance test with {iterations} iterations")
        
        # Create results array (reduced from 7 to 5 elements)
        from ctypes import c_double
        results = (c_double * 5)()
        
        self._library.performance_test(iterations, results)
        
        return {
            "iterations": iterations,
            "addr_gen_ms": round(results[0], 3),
            "addr_verify_ms": round(results[1], 3),
            "fast_verify_ms": round(results[2], 3),
            "onetime_sk_ms": round(results[3], 3),
            "trace_ms": round(results[4], 3),
            "scheme": "sitaiba",
            "note": "All times exclude hash computation overhead",
            "status": "completed"
        }
    
    # Data access methods
    def get_keys(self) -> List[Dict[str, Any]]:
        """Get all SITAIBA keys."""
        return self._keys
    
    def get_addresses(self) -> List[Dict[str, Any]]:
        """Get all SITAIBA addresses."""
        return self._addresses
    
    def get_dsks(self) -> List[Dict[str, Any]]:
        """Get all SITAIBA DSKs."""
        return self._dsks
    
