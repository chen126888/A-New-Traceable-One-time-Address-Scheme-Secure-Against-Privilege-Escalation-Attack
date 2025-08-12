"""
Scheme manager for handling multiple cryptographic schemes.
Provides unified interface to switch between stealth and sitaiba schemes.
"""
from typing import Dict, Any, Optional
import traceback


class SchemeManager:
    """Manager for multiple cryptographic schemes."""
    
    def __init__(self):
        self.current_scheme = 'stealth'  # Default scheme
        self.schemes = {}
        self._initialize_schemes()
    
    def _initialize_schemes(self):
        """Initialize all available schemes."""
        import sys
        import os
        # Add server directory to path
        server_dir = os.path.dirname(__file__)
        if server_dir not in sys.path:
            sys.path.insert(0, server_dir)
        
        try:
            # Initialize Stealth scheme
            from schemes.stealth.stealth_services import StealthServices
            self.schemes['stealth'] = StealthServices()
            print("✅ Stealth scheme initialized")
        except Exception as e:
            print(f"❌ Failed to initialize stealth scheme: {e}")
            if hasattr(e, '__traceback__'):
                traceback.print_exc()
        
        try:
            # Initialize SITAIBA scheme
            from schemes.sitaiba.sitaiba_services import SitaibaServices
            self.schemes['sitaiba'] = SitaibaServices()
            print("✅ SITAIBA scheme initialized")
        except Exception as e:
            print(f"❌ Failed to initialize SITAIBA scheme: {e}")
            if hasattr(e, '__traceback__'):
                traceback.print_exc()
    
    def get_available_schemes(self) -> list:
        """Get list of available schemes."""
        return list(self.schemes.keys())
    
    def get_current_scheme_name(self) -> str:
        """Get current scheme name."""
        return self.current_scheme
    
    def get_current_service(self):
        """Get current scheme service instance."""
        if self.current_scheme not in self.schemes:
            raise ValueError(f"Scheme '{self.current_scheme}' not available")
        return self.schemes[self.current_scheme]
    
    def switch_scheme(self, scheme_name: str) -> Dict[str, Any]:
        """Switch to a different scheme."""
        if scheme_name not in self.schemes:
            available = ', '.join(self.get_available_schemes())
            raise ValueError(f"Unknown scheme '{scheme_name}'. Available: {available}")
        
        old_scheme = self.current_scheme
        self.current_scheme = scheme_name
        
        return {
            "status": "switched",
            "old_scheme": old_scheme,
            "new_scheme": scheme_name,
            "available_schemes": self.get_available_schemes()
        }
    
    def get_scheme_capabilities(self, scheme_name: Optional[str] = None) -> Dict[str, Any]:
        """Get capabilities of a scheme."""
        if scheme_name is None:
            scheme_name = self.current_scheme
        
        if scheme_name not in self.schemes:
            raise ValueError(f"Unknown scheme '{scheme_name}'")
        
        service = self.schemes[scheme_name]
        
        # Check method availability
        capabilities = {
            "scheme_name": scheme_name,
            "has_setup": hasattr(service, 'setup_system'),
            "has_keygen": hasattr(service, 'generate_keypair'),
            "has_addrgen": hasattr(service, 'generate_address'),
            "has_dskgen": hasattr(service, 'generate_dsk'),
            "has_signing": hasattr(service, 'sign_message'),
            "has_verification": hasattr(service, 'verify_signature'),
            "has_tracing": hasattr(service, 'trace_identity'),
            "has_performance": hasattr(service, 'performance_test')
        }
        
        # Update capabilities based on scheme specifics
        if scheme_name == 'sitaiba':
            # SITAIBA scheme specific capabilities
            capabilities.update({
                "has_signing": False,           # SITAIBA doesn't support signing
                "has_verification": False,      # SITAIBA doesn't support verification
                "has_addr_recognition": True,   # SITAIBA supports address recognition
                "implemented": True             # SITAIBA is now fully implemented
            })
        elif scheme_name == 'stealth':
            # Stealth scheme specific capabilities
            capabilities.update({
                "has_addr_recognition": True,   # Stealth supports address recognition
                "implemented": True
            })
        else:
            capabilities["implemented"] = False
        
        return capabilities
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall scheme manager status."""
        return {
            "current_scheme": self.current_scheme,
            "available_schemes": self.get_available_schemes(),
            "current_capabilities": self.get_scheme_capabilities(),
            "schemes_status": {
                scheme: self.get_scheme_capabilities(scheme) 
                for scheme in self.get_available_schemes()
            }
        }
    
    # Unified method dispatching
    def setup_system(self, param_file: str) -> Dict[str, Any]:
        """Setup current scheme system."""
        service = self.get_current_service()
        result = service.setup_system(param_file)
        result["scheme"] = self.current_scheme
        return result
    
    def generate_keypair(self) -> Dict[str, Any]:
        """Generate keypair with current scheme."""
        service = self.get_current_service()
        result = service.generate_keypair()
        result["scheme"] = self.current_scheme
        return result
    
    def generate_address(self, key_index: int) -> Dict[str, Any]:
        """Generate address with current scheme."""
        service = self.get_current_service()
        result = service.generate_address(key_index)
        result["scheme"] = self.current_scheme
        return result
    
    def generate_dsk(self, address_index: int, key_index: int) -> Dict[str, Any]:
        """Generate DSK with current scheme."""
        service = self.get_current_service()
        result = service.generate_dsk(address_index, key_index)
        result["scheme"] = self.current_scheme
        return result
    
    def sign_message(self, *args, **kwargs) -> Dict[str, Any]:
        """Sign message with current scheme (if supported)."""
        capabilities = self.get_scheme_capabilities()
        if not capabilities.get("has_signing", False):
            return {
                "error": f"Scheme '{self.current_scheme}' doesn't support message signing",
                "scheme": self.current_scheme
            }
        
        service = self.get_current_service()
        result = service.sign_message(*args, **kwargs)
        result["scheme"] = self.current_scheme
        return result
    
    def verify_signature(self, *args, **kwargs) -> Dict[str, Any]:
        """Verify signature with current scheme (if supported)."""
        capabilities = self.get_scheme_capabilities()
        if not capabilities.get("has_verification", False):
            return {
                "error": f"Scheme '{self.current_scheme}' doesn't support signature verification",
                "scheme": self.current_scheme
            }
        
        service = self.get_current_service()
        result = service.verify_signature(*args, **kwargs)
        result["scheme"] = self.current_scheme
        return result
    
    def trace_identity(self, address_index: int) -> Dict[str, Any]:
        """Trace identity with current scheme."""
        service = self.get_current_service()
        result = service.trace_identity(address_index)
        result["scheme"] = self.current_scheme
        return result
    
    def performance_test(self, iterations: int = 100) -> Dict[str, Any]:
        """Run performance test with current scheme."""
        service = self.get_current_service()
        result = service.performance_test(iterations)
        result["scheme"] = self.current_scheme
        return result


# Global scheme manager instance
scheme_manager = SchemeManager()