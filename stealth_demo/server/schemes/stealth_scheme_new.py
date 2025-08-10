"""
Stealth Scheme implementation.
Wraps the Stealth cryptographic operations into the plugin architecture.
Stealth: Traceable Anonymous Transaction Scheme
"""
from typing import Dict, List, Any, Optional
from .base_scheme import BaseScheme, SchemeInfo
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stealth_library_wrapper import get_stealth_library
from stealth_utils import (
    get_stealth_element_size, bytes_to_hex_safe_fixed_stealth,
    hex_to_bytes_safe_stealth, format_stealth_key_display,
    format_stealth_signature_display, initialize_stealth_library
)


class StealthScheme(BaseScheme):
    """Implementation of the Stealth cryptographic scheme."""
    
    def __init__(self, scheme_info: SchemeInfo = None):
        if scheme_info is None:
            scheme_info = SchemeInfo(
                name="stealth",
                version="1.0.0",
                description="Traceable Anonymous Transaction Scheme with stealth addresses",
                capabilities=[
                    'setup', 'keygen', 'tracekeygen', 'addrgen', 'verify_addr', 
                    'dskgen', 'sign', 'verify', 'trace', 'performance'
                ],
                param_files=[
                    'a.param', 'a1.param', 'd105171-196-185.param', 'd159.param',
                    'd201.param', 'd224.param', 'd277699-175-167.param', 
                    'd278027-190-181.param', 'e.param', 'f.param', 'g149.param', 'i.param'
                ],
                author="Stealth Research Team"
            )
        super().__init__(scheme_info)
        
        # Stealth-specific storage
        self._keys: List[Dict] = []
        self._addresses: List[Dict] = []
        self._dsks: List[Dict] = []
        self._signatures: List[Dict] = []
        self._tracer_key: Optional[Dict] = None
        
        # Store reference to Stealth library
        self._library = None
    
    def get_info(self) -> SchemeInfo:
        """Get scheme information."""
        return self.info
    
    def setup_system(self, param_file: str) -> Dict[str, Any]:
        """Initialize the Stealth scheme with parameter file."""
        if not self.validate_param_file(param_file):
            raise ValueError(f"Parameter file {param_file} not supported by Stealth scheme")
        
        full_path = f"../param/pbc/{param_file}"
        
        print(f"🔧 Initializing Stealth with {full_path}")
        
        # Initialize library
        success = initialize_stealth_library(full_path)
        if not success:
            raise Exception("Stealth library initialization failed")
        
        self._library = get_stealth_library()
        
        if not self._library.is_initialized():
            raise Exception("Stealth library initialization verification failed")
        
        self.initialized = True
        self.current_param_file = param_file
        
        # Generate tracer key during setup
        tracer_key_info = self._generate_tracer_key()
        self._tracer_key = tracer_key_info
        
        # Clear existing data
        self._keys.clear()
        self._addresses.clear()
        self._dsks.clear()
        self._signatures.clear()
        
        g1_size = self._library.get_element_size_G1()
        zr_size = self._library.get_element_size_Zr()
        
        return {
            "status": "setup complete",
            "message": f"Stealth scheme initialized with {param_file}",
            "param_file": param_file,
            "scheme_name": self.info.name,
            "scheme_version": self.info.version,
            "g1_size": g1_size,
            "zr_size": zr_size,
            "tracer_key_available": self._tracer_key is not None,
            **tracer_key_info
        }
    
    def reset_system(self) -> Dict[str, Any]:
        """Reset the Stealth scheme state."""
        if self.initialized and self._library:
            self._library.reset_performance()
        
        # Clear all stored data
        self._keys.clear()
        self._addresses.clear()
        self._dsks.clear()
        self._signatures.clear()
        
        return {
            "status": "system reset",
            "message": "All keys, addresses, DSKs, and signatures cleared"
        }
    
    def _generate_tracer_key(self) -> Dict[str, Any]:
        """Generate tracer key for the system."""
        if not self._library or not self._library.is_initialized():
            raise Exception("Library not initialized")
        
        buf_size = get_stealth_element_size()
        TK_bytes, k_bytes = self._library.tracekeygen(buf_size)
        
        return {
            "tracer_public_key": TK_bytes.hex(),
            "tracer_private_key": k_bytes.hex(),
            "tracer_key_size": len(TK_bytes)
        }
    
    def generate_keypair(self, **kwargs) -> Dict[str, Any]:
        """Generate a new key pair (A, B, a, b)."""
        if not self.initialized or not self._library:
            raise Exception("Scheme not initialized")
        
        buf_size = get_stealth_element_size()
        A_bytes, B_bytes, a_bytes, b_bytes = self._library.keygen(buf_size)
        
        key_info = {
            "key_id": len(self._keys),
            "A": A_bytes.hex(),  # Public key A
            "B": B_bytes.hex(),  # Public key B  
            "a": a_bytes.hex(),  # Private key a
            "b": b_bytes.hex(),  # Private key b
            "created_at": self._get_timestamp()
        }
        
        self._keys.append(key_info)
        
        return {
            "status": "keypair generated",
            "key_id": key_info["key_id"],
            "public_key_A": format_stealth_key_display(A_bytes, "Public Key A"),
            "public_key_B": format_stealth_key_display(B_bytes, "Public Key B"),
            "private_key_a": format_stealth_key_display(a_bytes, "Private Key a"),
            "private_key_b": format_stealth_key_display(b_bytes, "Private Key b"),
            "key_size": len(A_bytes)
        }
    
    def generate_address(self, key_id: int, **kwargs) -> Dict[str, Any]:
        """Generate stealth address using specified key pair."""
        if not self.initialized or not self._library:
            raise Exception("Scheme not initialized")
        
        if key_id >= len(self._keys):
            raise ValueError(f"Key ID {key_id} not found")
        
        if not self._tracer_key:
            raise Exception("Tracer key not available")
        
        key_info = self._keys[key_id]
        
        # Convert hex to bytes
        A_bytes = hex_to_bytes_safe_stealth(key_info["A"])
        B_bytes = hex_to_bytes_safe_stealth(key_info["B"])
        TK_bytes = hex_to_bytes_safe_stealth(self._tracer_key["tracer_public_key"])
        
        buf_size = get_stealth_element_size()
        addr_bytes, r1_bytes, r2_bytes, c_bytes = self._library.addr_gen(A_bytes, B_bytes, TK_bytes, buf_size)
        
        addr_info = {
            "addr_id": len(self._addresses),
            "key_id": key_id,
            "address": addr_bytes.hex(),
            "R1": r1_bytes.hex(),
            "R2": r2_bytes.hex(),
            "C": c_bytes.hex(),
            "created_at": self._get_timestamp()
        }
        
        self._addresses.append(addr_info)
        
        return {
            "status": "address generated",
            "addr_id": addr_info["addr_id"],
            "address": format_stealth_key_display(addr_bytes, "Stealth Address"),
            "R1": format_stealth_key_display(r1_bytes, "R1 Component"),
            "R2": format_stealth_key_display(r2_bytes, "R2 Component"), 
            "C": format_stealth_key_display(c_bytes, "C Component"),
            "key_id": key_id
        }
    
    def verify_address(self, addr_id: int, key_id: int, **kwargs) -> Dict[str, Any]:
        """Verify stealth address (fast verification)."""
        if not self.initialized or not self._library:
            raise Exception("Scheme not initialized")
        
        if addr_id >= len(self._addresses):
            raise ValueError(f"Address ID {addr_id} not found")
        
        if key_id >= len(self._keys):
            raise ValueError(f"Key ID {key_id} not found")
        
        addr_info = self._addresses[addr_id]
        key_info = self._keys[key_id]
        
        # Convert hex to bytes
        R1_bytes = hex_to_bytes_safe_stealth(addr_info["R1"])
        B_bytes = hex_to_bytes_safe_stealth(key_info["B"])
        A_bytes = hex_to_bytes_safe_stealth(key_info["A"])
        C_bytes = hex_to_bytes_safe_stealth(addr_info["C"])
        a_bytes = hex_to_bytes_safe_stealth(key_info["a"])
        
        is_valid = self._library.addr_verify(R1_bytes, B_bytes, A_bytes, C_bytes, a_bytes)
        
        return {
            "status": "address verified",
            "addr_id": addr_id,
            "key_id": key_id,
            "is_valid": is_valid,
            "verification_method": "fast_verify"
        }
    
    def generate_dsk(self, addr_id: int, key_id: int, **kwargs) -> Dict[str, Any]:
        """Generate one-time secret key (DSK)."""
        if not self.initialized or not self._library:
            raise Exception("Scheme not initialized")
        
        if addr_id >= len(self._addresses):
            raise ValueError(f"Address ID {addr_id} not found")
        
        if key_id >= len(self._keys):
            raise ValueError(f"Key ID {key_id} not found")
        
        addr_info = self._addresses[addr_id]
        key_info = self._keys[key_id]
        
        # Convert hex to bytes
        addr_bytes = hex_to_bytes_safe_stealth(addr_info["address"])
        r1_bytes = hex_to_bytes_safe_stealth(addr_info["R1"])
        a_bytes = hex_to_bytes_safe_stealth(key_info["a"])
        b_bytes = hex_to_bytes_safe_stealth(key_info["b"])
        
        buf_size = get_stealth_element_size()
        dsk_bytes = self._library.dsk_gen(addr_bytes, r1_bytes, a_bytes, b_bytes, buf_size)
        
        dsk_info = {
            "dsk_id": len(self._dsks),
            "addr_id": addr_id,
            "key_id": key_id,
            "dsk": dsk_bytes.hex(),
            "created_at": self._get_timestamp()
        }
        
        self._dsks.append(dsk_info)
        
        return {
            "status": "DSK generated",
            "dsk_id": dsk_info["dsk_id"],
            "dsk": format_stealth_key_display(dsk_bytes, "One-time Secret Key"),
            "addr_id": addr_id,
            "key_id": key_id
        }
    
    def sign_message(self, message: str, dsk_id: int, **kwargs) -> Dict[str, Any]:
        """Sign message using DSK."""
        if not self.initialized or not self._library:
            raise Exception("Scheme not initialized")
        
        if dsk_id >= len(self._dsks):
            raise ValueError(f"DSK ID {dsk_id} not found")
        
        dsk_info = self._dsks[dsk_id]
        addr_info = self._addresses[dsk_info["addr_id"]]
        
        # Convert hex to bytes
        addr_bytes = hex_to_bytes_safe_stealth(addr_info["address"])
        dsk_bytes = hex_to_bytes_safe_stealth(dsk_info["dsk"])
        
        buf_size = get_stealth_element_size()
        q_sigma_bytes, h_bytes = self._library.sign_with_dsk(addr_bytes, dsk_bytes, message, buf_size)
        
        sig_info = {
            "sig_id": len(self._signatures),
            "dsk_id": dsk_id,
            "addr_id": dsk_info["addr_id"],
            "message": message,
            "q_sigma": q_sigma_bytes.hex(),
            "h": h_bytes.hex(),
            "created_at": self._get_timestamp()
        }
        
        self._signatures.append(sig_info)
        
        return {
            "status": "message signed",
            "sig_id": sig_info["sig_id"],
            "message": message,
            "signature": format_stealth_signature_display(q_sigma_bytes, h_bytes),
            "dsk_id": dsk_id
        }
    
    def verify_signature(self, sig_id: int, **kwargs) -> Dict[str, Any]:
        """Verify signature."""
        if not self.initialized or not self._library:
            raise Exception("Scheme not initialized")
        
        if sig_id >= len(self._signatures):
            raise ValueError(f"Signature ID {sig_id} not found")
        
        sig_info = self._signatures[sig_id]
        addr_info = self._addresses[sig_info["addr_id"]]
        
        # Convert hex to bytes
        addr_bytes = hex_to_bytes_safe_stealth(addr_info["address"])
        r2_bytes = hex_to_bytes_safe_stealth(addr_info["R2"])
        c_bytes = hex_to_bytes_safe_stealth(addr_info["C"])
        h_bytes = hex_to_bytes_safe_stealth(sig_info["h"])
        q_sigma_bytes = hex_to_bytes_safe_stealth(sig_info["q_sigma"])
        
        is_valid = self._library.verify(addr_bytes, r2_bytes, c_bytes, sig_info["message"], h_bytes, q_sigma_bytes)
        
        return {
            "status": "signature verified",
            "sig_id": sig_id,
            "message": sig_info["message"],
            "is_valid": is_valid
        }
    
    def trace_identity(self, addr_id: int, **kwargs) -> Dict[str, Any]:
        """Trace identity to recover public key."""
        if not self.initialized or not self._library:
            raise Exception("Scheme not initialized")
        
        if addr_id >= len(self._addresses):
            raise ValueError(f"Address ID {addr_id} not found")
        
        if not self._tracer_key:
            raise Exception("Tracer key not available")
        
        addr_info = self._addresses[addr_id]
        
        # Convert hex to bytes
        addr_bytes = hex_to_bytes_safe_stealth(addr_info["address"])
        r1_bytes = hex_to_bytes_safe_stealth(addr_info["R1"])
        r2_bytes = hex_to_bytes_safe_stealth(addr_info["R2"])
        c_bytes = hex_to_bytes_safe_stealth(addr_info["C"])
        k_bytes = hex_to_bytes_safe_stealth(self._tracer_key["tracer_private_key"])
        
        buf_size = get_stealth_element_size()
        b_recovered_bytes = self._library.trace(addr_bytes, r1_bytes, r2_bytes, c_bytes, k_bytes, buf_size)
        
        # Find matching key
        original_key_id = addr_info["key_id"]
        original_B = self._keys[original_key_id]["B"] if original_key_id < len(self._keys) else None
        
        return {
            "status": "identity traced",
            "addr_id": addr_id,
            "recovered_B": format_stealth_key_display(b_recovered_bytes, "Recovered Public Key B"),
            "original_B": original_B,
            "match": original_B == b_recovered_bytes.hex() if original_B else False,
            "original_key_id": original_key_id
        }
    
    def get_performance_stats(self, iterations: int = 100, **kwargs) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.initialized or not self._library:
            raise Exception("Scheme not initialized")
        
        stats = self._library.performance_test(iterations)
        
        return {
            "status": "performance test completed",
            "iterations": iterations,
            "results": {
                "address_generation_avg_ms": round(stats.get('addr_gen_avg', 0), 3),
                "address_verification_avg_ms": round(stats.get('addr_verify_avg', 0), 3),
                "fast_verification_avg_ms": round(stats.get('fast_verify_avg', 0), 3),
                "onetime_sk_generation_avg_ms": round(stats.get('onetime_sk_avg', 0), 3),
                "signing_avg_ms": round(stats.get('sign_avg', 0), 3),
                "verification_avg_ms": round(stats.get('verify_avg', 0), 3),
                "tracing_avg_ms": round(stats.get('trace_avg', 0), 3)
            }
        }
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current state summary."""
        return {
            "scheme_name": self.info.name,
            "initialized": self.initialized,
            "param_file": self.current_param_file,
            "keys_count": len(self._keys),
            "addresses_count": len(self._addresses),
            "dsks_count": len(self._dsks),
            "signatures_count": len(self._signatures),
            "tracer_key_available": self._tracer_key is not None,
            "capabilities": self.info.capabilities
        }
    
    # Data access methods for compatibility
    def get_keys(self) -> List[Dict[str, Any]]:
        """Get all stealth keys."""
        return self._keys
    
    def get_addresses(self) -> List[Dict[str, Any]]:
        """Get all stealth addresses."""
        return self._addresses
    
    def get_dsks(self) -> List[Dict[str, Any]]:
        """Get all stealth DSKs."""
        return self._dsks
    
    def get_signatures(self) -> List[Dict[str, Any]]:
        """Get all stealth signatures."""
        return self._signatures
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()