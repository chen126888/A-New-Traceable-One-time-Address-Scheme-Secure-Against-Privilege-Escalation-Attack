"""
Scheme Manager for handling multiple cryptographic schemes.
Provides registration, selection, and management of different schemes.
"""
from typing import Dict, List, Optional, Type
from .base_scheme import BaseScheme, SchemeInfo


class SchemeManager:
    """
    Manages multiple cryptographic schemes.
    Handles registration, selection, and routing of operations to active scheme.
    """
    
    def __init__(self):
        self._schemes: Dict[str, Type[BaseScheme]] = {}
        self._active_scheme: Optional[BaseScheme] = None
        self._active_scheme_name: Optional[str] = None
    
    def register_scheme(self, scheme_class: Type[BaseScheme]):
        """Register a new scheme class."""
        # Create temporary instance to get info
        temp_instance = scheme_class()
        info = temp_instance.get_info()
        
        self._schemes[info.name] = scheme_class
        print(f"📝 Registered scheme: {info.name}")
    
    def get_available_schemes(self) -> List[SchemeInfo]:
        """Get information about all available schemes."""
        schemes_info = []
        for scheme_class in self._schemes.values():
            temp_instance = scheme_class()
            schemes_info.append(temp_instance.get_info())
        return schemes_info
    
    def activate_scheme(self, scheme_name: str) -> bool:
        """Activate a specific scheme."""
        if scheme_name not in self._schemes:
            raise ValueError(f"Unknown scheme: {scheme_name}")
        
        scheme_class = self._schemes[scheme_name]
        self._active_scheme = scheme_class()
        self._active_scheme_name = scheme_name
        
        print(f"✅ Activated scheme: {scheme_name}")
        return True
    
    def get_active_scheme(self) -> Optional[BaseScheme]:
        """Get the currently active scheme."""
        return self._active_scheme
    
    def get_active_scheme_name(self) -> Optional[str]:
        """Get the name of currently active scheme."""
        return self._active_scheme_name
    
    def is_scheme_active(self) -> bool:
        """Check if any scheme is currently active."""
        return self._active_scheme is not None
    
    def get_scheme_info(self, scheme_name: str) -> Optional[SchemeInfo]:
        """Get information about a specific scheme."""
        if scheme_name not in self._schemes:
            return None
        
        scheme_class = self._schemes[scheme_name]
        temp_instance = scheme_class()
        return temp_instance.get_info()
    
    def supports_capability(self, capability: str) -> bool:
        """Check if active scheme supports a capability."""
        if not self._active_scheme:
            return False
        return self._active_scheme.supports_capability(capability)
    
    def reset_active_scheme(self):
        """Reset the active scheme."""
        self._active_scheme = None
        self._active_scheme_name = None
    
    # Proxy methods to active scheme
    def setup_system(self, param_file: str) -> Dict:
        """Setup system using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.setup_system(param_file)
    
    def reset_system(self) -> Dict:
        """Reset system using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.reset_system()
    
    def get_status(self) -> Dict:
        """Get status from active scheme."""
        if not self._active_scheme:
            return {
                "active_scheme": None,
                "initialized": False,
                "available_schemes": [info.name for info in self.get_available_schemes()]
            }
        
        status = self._active_scheme.get_status()
        status.update({
            "active_scheme": self._active_scheme_name,
            "available_schemes": [info.name for info in self.get_available_schemes()]
        })
        return status
    
    def generate_keypair(self, **kwargs) -> Dict:
        """Generate keypair using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.generate_keypair(**kwargs)
    
    def generate_address(self, **kwargs) -> Dict:
        """Generate address using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.generate_address(**kwargs)
    
    def verify_address(self, **kwargs) -> Dict:
        """Verify address using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.verify_address(**kwargs)
    
    def generate_dsk(self, **kwargs) -> Dict:
        """Generate DSK using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.generate_dsk(**kwargs)
    
    def sign_message(self, **kwargs) -> Dict:
        """Sign message using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.sign_message(**kwargs)
    
    def verify_signature(self, **kwargs) -> Dict:
        """Verify signature using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.verify_signature(**kwargs)
    
    def trace_identity(self, **kwargs) -> Dict:
        """Trace identity using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.trace_identity(**kwargs)
    
    def performance_test(self, **kwargs) -> Dict:
        """Run performance test using active scheme."""
        if not self._active_scheme:
            raise RuntimeError("No active scheme")
        return self._active_scheme.performance_test(**kwargs)
    
    # Data access methods
    def get_keys(self) -> List[Dict]:
        """Get keys from active scheme."""
        if not self._active_scheme:
            return []
        return self._active_scheme.get_keys()
    
    def get_keys_normalized(self) -> List[Dict]:
        """Get keys in standardized format from active scheme."""
        if not self._active_scheme:
            return []
        return self._active_scheme.get_keys_normalized()
    
    def get_addresses(self) -> List[Dict]:
        """Get addresses from active scheme."""
        if not self._active_scheme:
            return []
        return self._active_scheme.get_addresses()
    
    def get_dsks(self) -> List[Dict]:
        """Get DSKs from active scheme."""
        if not self._active_scheme:
            return []
        return self._active_scheme.get_dsks()
    
    def get_signatures(self) -> List[Dict]:
        """Get signatures from active scheme."""
        if not self._active_scheme:
            return []
        return self._active_scheme.get_signatures()


# Global scheme manager instance
scheme_manager = SchemeManager()