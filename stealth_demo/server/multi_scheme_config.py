"""
Multi-scheme configuration module for the cryptographic demo application.
Hangles parameter files, system initialization, and data management for multiple schemes.
"""
import os
import glob
from typing import Dict, List, Optional


# Get the absolute path to the directory containing this file
_current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the absolute path to the 'param' directory
_param_base_dir = os.path.join(_current_dir, '..', 'param')


class MultiSchemeConfig:
    """Configuration and state management for multiple cryptographic schemes."""
    
    def __init__(self):
        # Multi-scheme data storage - separated by scheme
        self.schemes_data = {
            'stealth': {
                'system_initialized': False,
                'current_param_file': None,
                'trace_key': None,
                'key_list': [],
                'address_list': [],
                'dsk_list': [],
                'tx_message_list': [],  # stealth supports signing
                'dsk_functions_available': False
            },
            'sitaiba': {
                'system_initialized': False,
                'current_param_file': None,
                'trace_key': None,
                'key_list': [],
                'address_list': [],
                'dsk_list': [],
                # no tx_message_list - sitaiba doesn't support signing
                'dsk_functions_available': False
            }
        }
        
        # Global settings
        self.current_scheme = 'stealth'  # Default scheme
    
    def get_current_data(self) -> Dict:
        """Get data for the current scheme."""
        return self.schemes_data[self.current_scheme]
    
    def get_scheme_data(self, scheme_name: str) -> Dict:
        """Get data for a specific scheme."""
        if scheme_name not in self.schemes_data:
            raise ValueError(f"Unknown scheme: {scheme_name}")
        return self.schemes_data[scheme_name]
    
    def set_current_scheme(self, scheme_name: str):
        """Set the current active scheme."""
        if scheme_name not in self.schemes_data:
            raise ValueError(f"Unknown scheme: {scheme_name}")
        self.current_scheme = scheme_name
    
    # Parameter file management (shared across schemes)
    def get_param_files(self) -> Dict:
        """Get list of available parameter files."""
        # Use the pre-calculated absolute path
        if not os.path.exists(_param_base_dir):
            raise FileNotFoundError(f"Parameter directory not found at {_param_base_dir}")
        
        param_files = []
        for file_path in glob.glob(os.path.join(_param_base_dir, "*.param")):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            param_files.append({
                "name": file_name,
                "path": file_path,
                "size": file_size
            })
        
        param_files.sort(key=lambda x: x["name"])
        
        current_data = self.get_current_data()
        return {
            "param_files": param_files,
            "current": current_data['current_param_file'],
            "current_scheme": self.current_scheme
        }
    
    def validate_param_file(self, param_file: str) -> str:
        """Validate parameter file exists and return full path."""
        # Use the pre-calculated absolute path
        full_path = os.path.join(_param_base_dir, param_file)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Parameter file not found: {param_file} at {full_path}")
        return full_path
    
    # Scheme-specific state management
    def set_initialized(self, param_file: str, trace_key: Dict, scheme_name: Optional[str] = None):
        """Mark system as initialized for current or specified scheme."""
        if scheme_name is None:
            scheme_name = self.current_scheme
        
        scheme_data = self.get_scheme_data(scheme_name)
        scheme_data['system_initialized'] = True
        scheme_data['current_param_file'] = param_file
        scheme_data['trace_key'] = trace_key
    
    def ensure_initialized(self, scheme_name: Optional[str] = None):
        """Ensure the system is initialized for current or specified scheme."""
        if scheme_name is None:
            scheme_name = self.current_scheme
        
        scheme_data = self.get_scheme_data(scheme_name)
        if not scheme_data['system_initialized']:
            raise Exception(f"Scheme '{scheme_name}' not initialized. Please run setup first.")
    
    def reset_scheme(self, scheme_name: Optional[str] = None):
        """Reset state for current or specified scheme."""
        if scheme_name is None:
            scheme_name = self.current_scheme
        
        scheme_data = self.get_scheme_data(scheme_name)
        scheme_data['key_list'].clear()
        scheme_data['address_list'].clear()
        scheme_data['dsk_list'].clear()
        
        # Only clear tx_message_list if it exists (stealth has it, sitaiba doesn't)
        if 'tx_message_list' in scheme_data:
            scheme_data['tx_message_list'].clear()
        
        scheme_data['trace_key'] = None
        scheme_data['system_initialized'] = False
        scheme_data['current_param_file'] = None
    
    def reset_all_schemes(self):
        """Reset all schemes data."""
        for scheme_name in self.schemes_data.keys():
            self.reset_scheme(scheme_name)
    
    def get_status(self, scheme_name: Optional[str] = None) -> Dict:
        """Get current system status for current or specified scheme."""
        if scheme_name is None:
            scheme_name = self.current_scheme
        
        scheme_data = self.get_scheme_data(scheme_name)
        
        status = {
            "scheme": scheme_name,
            "initialized": scheme_data['system_initialized'],
            "param_file": scheme_data['current_param_file'],
            "trace_key_set": scheme_data['trace_key'] is not None,
            "keys_count": len(scheme_data['key_list']),
            "addresses_count": len(scheme_data['address_list']),
            "dsks_count": len(scheme_data['dsk_list']),
            "dsk_functions_available": scheme_data['dsk_functions_available'],
            "architecture": f"multi_scheme_{scheme_name}"
        }
        
        # Add tx_messages_count if the scheme supports it
        if 'tx_message_list' in scheme_data:
            status["tx_messages_count"] = len(scheme_data['tx_message_list'])
        
        return status
    
    def get_all_status(self) -> Dict:
        """Get status for all schemes."""
        return {
            "current_scheme": self.current_scheme,
            "schemes": {
                scheme_name: self.get_status(scheme_name)
                for scheme_name in self.schemes_data.keys()
            }
        }
    
    # Convenience properties for current scheme (backward compatibility)
    @property
    def system_initialized(self) -> bool:
        """Check if current scheme is initialized."""
        return self.get_current_data()['system_initialized']
    
    @property
    def current_param_file(self) -> Optional[str]:
        """Get current scheme's param file."""
        return self.get_current_data()['current_param_file']
    
    @property
    def trace_key(self) -> Optional[Dict]:
        """Get current scheme's trace key."""
        return self.get_current_data()['trace_key']
    
    @property
    def key_list(self) -> List[Dict]:
        """Get current scheme's key list."""
        return self.get_current_data()['key_list']
    
    @property
    def address_list(self) -> List[Dict]:
        """Get current scheme's address list."""
        return self.get_current_data()['address_list']
    
    @property
    def dsk_list(self) -> List[Dict]:
        """Get current scheme's DSK list."""
        return self.get_current_data()['dsk_list']
    
    @property
    def tx_message_list(self) -> List[Dict]:
        """Get current scheme's transaction message list (if supported)."""
        current_data = self.get_current_data()
        return current_data.get('tx_message_list', [])
    
    @property
    def dsk_functions_available(self) -> bool:
        """Check if current scheme has DSK functions available."""
        return self.get_current_data()['dsk_functions_available']
    
    # Backward compatibility methods
    def reset(self):
        """Reset current scheme (backward compatibility)."""
        self.reset_scheme()
    
    def ensure_initialized_legacy(self):
        """Legacy ensure_initialized method."""
        self.ensure_initialized()


# Global configuration instance
config = MultiSchemeConfig()
