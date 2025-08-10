"""
Example New Cryptographic Scheme implementation.
Demonstrates how to add a new scheme with different capabilities.
This scheme has no signing/verification but has different key and address operations.
"""
from typing import Dict, List, Any, Optional
from .base_scheme import BaseScheme, SchemeInfo
import random
import hashlib
import time


class ExampleNewScheme(BaseScheme):
    """
    Example implementation of a new cryptographic scheme.
    This scheme demonstrates:
    - Different key generation (single key instead of key pairs)
    - Different address format (hash-based instead of group elements)
    - No signing/verification capabilities
    - Different performance characteristics
    """
    
    def __init__(self, scheme_info: SchemeInfo = None):
        if scheme_info is None:
            scheme_info = SchemeInfo(
                name="example_new",
                version="1.0.0",
                description="Example New Scheme with hash-based addresses (no signing)",
                capabilities=[
                    'setup', 'keygen', 'addrgen', 'verify_addr', 'performance'
                ],
                param_files=[
                    'example.param', 'test.param'  # Different parameter files
                ],
                author="Demo Team"
            )
        super().__init__(scheme_info)
        
        # Scheme-specific storage
        self._keys: List[Dict] = []
        self._addresses: List[Dict] = []
        self._master_secret: Optional[str] = None
        self._scheme_params: Optional[Dict] = None
    
    def get_info(self) -> SchemeInfo:
        """Get scheme information."""
        return self.info
    
    def setup_system(self, param_file: str) -> Dict[str, Any]:
        """Initialize the example scheme with parameter file."""
        if not self.validate_param_file(param_file):
            raise ValueError(f"Parameter file {param_file} not supported by example scheme")
        
        print(f"🔧 Initializing Example New Scheme with {param_file}")
        
        # Simulate parameter loading (in real scheme, this would load actual crypto parameters)
        self._scheme_params = {
            "hash_algorithm": "sha256",
            "key_length": 32,
            "address_format": "hash-based",
            "param_file": param_file
        }
        
        # Generate master secret for this session
        self._master_secret = hashlib.sha256(f"master_secret_{param_file}_{time.time()}".encode()).hexdigest()
        
        self.initialized = True
        self.current_param_file = param_file
        
        return {
            "status": "setup complete",
            "message": f"Example New Scheme initialized with {param_file}",
            "param_file": param_file,
            "scheme_name": self.info.name,
            "scheme_version": self.info.version,
            "hash_algorithm": self._scheme_params["hash_algorithm"],
            "key_length": self._scheme_params["key_length"],
            "master_secret_hash": hashlib.sha256(self._master_secret.encode()).hexdigest()[:16]
        }
    
    def reset_system(self) -> Dict[str, Any]:
        """Reset the example scheme state."""
        self._keys.clear()
        self._addresses.clear()
        self._master_secret = None
        self._scheme_params = None
        self.initialized = False
        self.current_param_file = None
        
        return {
            "status": "reset complete", 
            "message": "Example New Scheme state has been reset",
            "scheme_name": self.info.name,
            "keys_count": 0,
            "addresses_count": 0
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current example scheme status."""
        return {
            "initialized": self.initialized,
            "param_file": self.current_param_file,
            "scheme_name": self.info.name,
            "scheme_version": self.info.version,
            "capabilities": self.info.capabilities,
            "keys_count": len(self._keys),
            "addresses_count": len(self._addresses),
            "hash_algorithm": self._scheme_params.get("hash_algorithm") if self._scheme_params else None,
            "key_length": self._scheme_params.get("key_length") if self._scheme_params else None,
            "has_master_secret": self._master_secret is not None
        }
    
    def generate_keypair(self, **kwargs) -> Dict[str, Any]:
        """Generate a single key (not a pair) for the example scheme."""
        if not self.initialized:
            raise RuntimeError("Scheme not initialized")
        
        # Generate a single key using hash of master secret + index
        key_index = len(self._keys)
        key_seed = f"{self._master_secret}_{key_index}_{time.time()}"
        key_hash = hashlib.sha256(key_seed.encode()).hexdigest()
        
        # In a real scheme, this would be proper key generation
        key_data = {
            "index": key_index,
            "id": f"key_{key_index}",
            "key_hex": key_hash,
            "key_type": "single_key",  # Different from stealth's key pairs
            "generated_at": int(time.time()),
            "param_file": self.current_param_file,
            "status": "generated"
        }
        
        self._keys.append(key_data)
        return key_data
    
    def generate_address(self, key_index: int, **kwargs) -> Dict[str, Any]:
        """Generate hash-based address (different from stealth's group-based addresses)."""
        if not self.initialized:
            raise RuntimeError("Scheme not initialized")
        
        if key_index < 0 or key_index >= len(self._keys):
            raise ValueError(f"Invalid key_index: {key_index}")
        
        selected_key = self._keys[key_index]
        
        # Generate address using different algorithm (hash-based)
        address_index = len(self._addresses)
        nonce = random.randint(1000000, 9999999)  # Random nonce
        
        address_seed = f"{selected_key['key_hex']}_{nonce}_{address_index}"
        address_hash = hashlib.sha256(address_seed.encode()).hexdigest()
        
        # Different address format with verification data
        verification_data = hashlib.sha256(f"verify_{address_hash}".encode()).hexdigest()[:16]
        
        address_data = {
            "index": address_index,
            "id": f"addr_{address_index}",
            "address_hex": address_hash,
            "verification_hex": verification_data,
            "nonce": nonce,
            "key_index": key_index,
            "key_id": selected_key['id'],
            "address_type": "hash_based",  # Different type
            "generated_at": int(time.time()),
            "status": "generated"
        }
        
        self._addresses.append(address_data)
        return address_data
    
    def verify_address(self, address_index: int, key_index: int, **kwargs) -> Dict[str, Any]:
        """Verify hash-based address (different verification algorithm)."""
        if not self.initialized:
            raise RuntimeError("Scheme not initialized")
        
        if address_index < 0 or address_index >= len(self._addresses):
            raise ValueError(f"Invalid address_index: {address_index}")
        
        if key_index < 0 or key_index >= len(self._keys):
            raise ValueError(f"Invalid key_index: {key_index}")
        
        address_data = self._addresses[address_index]
        key_data = self._keys[key_index]
        
        # Different verification: recompute address and compare
        expected_seed = f"{key_data['key_hex']}_{address_data['nonce']}_{address_index}"
        expected_hash = hashlib.sha256(expected_seed.encode()).hexdigest()
        
        is_valid = (expected_hash == address_data['address_hex'])
        is_owner = (address_data['key_index'] == key_index)
        
        return {
            "valid": is_valid,
            "address_index": address_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "is_owner": is_owner,
            "verification_method": "hash_recomputation",
            "status": "valid" if is_valid else "invalid"
        }
    
    def performance_test(self, iterations: int = 100, **kwargs) -> Dict[str, Any]:
        """Run performance test for the example scheme."""
        if not self.initialized:
            raise RuntimeError("Scheme not initialized")
        
        iterations = min(iterations, 1000)  # Limit iterations
        
        print(f"🧪 Running Example Scheme performance test with {iterations} iterations")
        
        # Measure key generation
        start_time = time.time()
        temp_keys = []
        for i in range(iterations):
            key_seed = f"test_key_{i}_{time.time()}"
            key_hash = hashlib.sha256(key_seed.encode()).hexdigest()
            temp_keys.append(key_hash)
        keygen_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Measure address generation
        start_time = time.time()
        for i in range(iterations):
            nonce = random.randint(1000000, 9999999)
            address_seed = f"{temp_keys[0]}_{nonce}_{i}"
            address_hash = hashlib.sha256(address_seed.encode()).hexdigest()
        addrgen_time = (time.time() - start_time) * 1000
        
        # Measure verification
        start_time = time.time()
        test_address = hashlib.sha256(f"{temp_keys[0]}_1234567_0".encode()).hexdigest()
        for i in range(iterations):
            # Simulate verification computation
            verify_seed = f"{temp_keys[0]}_1234567_0"
            verify_hash = hashlib.sha256(verify_seed.encode()).hexdigest()
            result = (verify_hash == test_address)
        verify_time = (time.time() - start_time) * 1000
        
        return {
            "iterations": iterations,
            "keygen_ms": round(keygen_time, 3),
            "addrgen_ms": round(addrgen_time, 3), 
            "verify_ms": round(verify_time, 3),
            "scheme_name": self.info.name,
            "note": "Hash-based operations (different from stealth scheme)",
            "status": "completed"
        }
    
    # Data access methods
    def get_keys(self) -> List[Dict[str, Any]]:
        """Get all keys from example scheme."""
        return self._keys
    
    def get_addresses(self) -> List[Dict[str, Any]]:
        """Get all addresses from example scheme."""
        return self._addresses
    
    def get_dsks(self) -> List[Dict[str, Any]]:
        """Get DSKs (not applicable for this scheme)."""
        return []
    
    def get_signatures(self) -> List[Dict[str, Any]]:
        """Get signatures (not applicable for this scheme)."""
        return []