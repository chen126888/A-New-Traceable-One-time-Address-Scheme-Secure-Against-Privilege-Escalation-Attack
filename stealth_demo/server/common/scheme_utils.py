"""
Scheme-aware utility factory and abstract base classes.
Handles scheme-specific implementations while providing unified interface.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

# Correct relative import for multi_scheme_config
from ..multi_scheme_config import config
# Correct relative import for base_utils
from .base_utils import create_buffer, create_multiple_buffers


class SchemeUtilsBase(ABC):
    """
    Abstract base class for scheme-specific utility implementations.
    Each scheme should inherit from this and implement the abstract methods.
    """
    
    @abstractmethod
    def get_element_size(self) -> int:
        """Get element sizes for buffer allocation (scheme-specific logic)."""
        pass
    
    @abstractmethod
    def bytes_to_hex_safe_fixed(self, buf, element_type: str = 'G1') -> str:
        """Convert buffer to hex string (scheme-specific handling)."""
        pass
    
    @abstractmethod
    def find_matching_key(self, target_hex: str) -> Optional[Dict[str, Any]]:
        """Find key with matching hex value (scheme-specific matching logic)."""
        pass
    
    def create_buffer_with_scheme_size(self, size: Optional[int] = None):
        """Create buffer using scheme-specific size if not provided."""
        if size is None:
            size = self.get_element_size()
        
        # Use the shared base implementation
        return create_buffer(size)
    
    def create_multiple_buffers_with_scheme_size(self, count: int, size: Optional[int] = None):
        """Create multiple buffers using scheme-specific size if not provided."""
        if size is None:
            size = self.get_element_size()
        
        # Use the shared base implementation
        return create_multiple_buffers(count, size)


class SchemeUtilsFactory:
    """
    Factory class to get the appropriate utility implementation for each scheme.
    """
    
    _instances = {}
    
    @staticmethod
    def get_utils(scheme_name: str) -> SchemeUtilsBase:
        """
        Get utility instance for the specified scheme.
        
        Args:
            scheme_name: Name of the cryptographic scheme
            
        Returns:
            SchemeUtilsBase: Scheme-specific utility implementation
            
        Raises:
            ValueError: If scheme is not supported
        """
        # Use singleton pattern to avoid repeated imports
        if scheme_name not in SchemeUtilsFactory._instances:
            if scheme_name == 'stealth':
                from ..schemes.stealth.stealth_utils import StealthUtils
                SchemeUtilsFactory._instances[scheme_name] = StealthUtils()
            elif scheme_name == 'sitaiba':
                from ..schemes.sitaiba.sitaiba_utils import SitaibaUtils
                SchemeUtilsFactory._instances[scheme_name] = SitaibaUtils()
            else:
                raise ValueError(f"Unknown scheme: {scheme_name}")
        
        return SchemeUtilsFactory._instances[scheme_name]
    
    @staticmethod
    def clear_cache():
        """Clear the factory cache (useful for testing)."""
        SchemeUtilsFactory._instances.clear()


# Convenience functions that automatically use the current scheme
def get_current_scheme_utils() -> SchemeUtilsBase:
    """Get utility instance for the currently active scheme."""
    # Removed sys.path modification
    return SchemeUtilsFactory.get_utils(config.current_scheme)


def get_element_size() -> int:
    """Get element size for current scheme."""
    return get_current_scheme_utils().get_element_size()


def bytes_to_hex_safe_fixed(buf, element_type: str = 'G1') -> str:
    """Convert buffer to hex for current scheme."""
    return get_current_scheme_utils().bytes_to_hex_safe_fixed(buf, element_type)


def find_matching_key(target_hex: str) -> Optional[Dict[str, Any]]:
    """Find matching key using current scheme logic."""
    return get_current_scheme_utils().find_matching_key(target_hex)
