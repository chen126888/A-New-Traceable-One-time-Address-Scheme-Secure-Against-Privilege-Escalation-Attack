"""
Base classes and interfaces for cryptographic schemes.
Defines the common interface that all schemes must implement.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SchemeInfo:
    """Information about a cryptographic scheme."""
    name: str
    version: str
    description: str
    capabilities: List[str]  # e.g., ['keygen', 'addrgen', 'sign', 'verify', 'trace']
    param_files: List[str]   # Supported parameter files
    author: str = "Unknown"
    

class BaseScheme(ABC):
    """
    Abstract base class for all cryptographic schemes.
    Each scheme must implement this interface.
    """
    
    def __init__(self, scheme_info: SchemeInfo):
        self.info = scheme_info
        self.initialized = False
        self.current_param_file: Optional[str] = None
        
    @abstractmethod
    def get_info(self) -> SchemeInfo:
        """Get scheme information."""
        pass
    
    @abstractmethod
    def setup_system(self, param_file: str) -> Dict[str, Any]:
        """Initialize the scheme with parameter file."""
        pass
    
    @abstractmethod
    def reset_system(self) -> Dict[str, Any]:
        """Reset the scheme state."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current scheme status."""
        pass
    
    # Core cryptographic operations (implement only if supported)
    def generate_keypair(self) -> Dict[str, Any]:
        """Generate a key pair."""
        raise NotImplementedError(f"Keygen not supported in {self.info.name}")
    
    def generate_address(self, **kwargs) -> Dict[str, Any]:
        """Generate address."""
        raise NotImplementedError(f"Address generation not supported in {self.info.name}")
    
    def verify_address(self, **kwargs) -> Dict[str, Any]:
        """Verify address."""
        raise NotImplementedError(f"Address verification not supported in {self.info.name}")
    
    def generate_dsk(self, **kwargs) -> Dict[str, Any]:
        """Generate DSK."""
        raise NotImplementedError(f"DSK generation not supported in {self.info.name}")
    
    def sign_message(self, **kwargs) -> Dict[str, Any]:
        """Sign message."""
        raise NotImplementedError(f"Message signing not supported in {self.info.name}")
    
    def verify_signature(self, **kwargs) -> Dict[str, Any]:
        """Verify signature."""
        raise NotImplementedError(f"Signature verification not supported in {self.info.name}")
    
    def trace_identity(self, **kwargs) -> Dict[str, Any]:
        """Trace identity."""
        raise NotImplementedError(f"Identity tracing not supported in {self.info.name}")
    
    def performance_test(self, **kwargs) -> Dict[str, Any]:
        """Run performance test."""
        raise NotImplementedError(f"Performance test not supported in {self.info.name}")
    
    # Data management
    def get_keys(self) -> List[Dict[str, Any]]:
        """Get all keys."""
        return []
    
    def get_addresses(self) -> List[Dict[str, Any]]:
        """Get all addresses."""
        return []
    
    def get_dsks(self) -> List[Dict[str, Any]]:
        """Get all DSKs."""
        return []
    
    def get_signatures(self) -> List[Dict[str, Any]]:
        """Get all signatures."""
        return []
    
    # Normalized data management for frontend compatibility
    def get_keys_normalized(self) -> List[Dict[str, Any]]:
        """Get keys in standardized format for frontend."""
        raw_keys = self.get_keys()
        return self._normalize_keys(raw_keys)
    
    def _normalize_keys(self, raw_keys: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize keys to standardized format. Each scheme should override this.
        Standard format:
        {
            "id": str,                    # Unique identifier
            "index": int,                 # Numeric index
            "scheme": str,                # Scheme name
            "public_key_A": str,          # Standardized field name
            "public_key_B": str,          # Standardized field name  
            "private_key_a": str,         # Standardized field name
            "private_key_b": str,         # Standardized field name
            "created_at": str,            # Optional timestamp
            # Scheme-specific fields can be added as needed
        }
        """
        # Default implementation - pass through raw keys
        return raw_keys
    
    # Utility methods
    def supports_capability(self, capability: str) -> bool:
        """Check if scheme supports a specific capability."""
        return capability in self.info.capabilities
    
    def validate_param_file(self, param_file: str) -> bool:
        """Validate if parameter file is supported."""
        return param_file in self.info.param_files