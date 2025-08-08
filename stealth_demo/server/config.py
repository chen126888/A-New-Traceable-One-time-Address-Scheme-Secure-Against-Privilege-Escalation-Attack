"""
Configuration and initialization module for the stealth demo application.
Handles parameter files, system initialization, and global state management.
"""
import os
import glob
from typing import Dict, List, Optional


class SteuthConfig:
    """Configuration and state management for the stealth application."""
    
    def __init__(self):
        self.system_initialized = False
        self.current_param_file: Optional[str] = None
        self.trace_key: Optional[Dict] = None
        
        # Data storage
        self.key_list: List[Dict] = []
        self.address_list: List[Dict] = []
        self.dsk_list: List[Dict] = []
        self.tx_message_list: List[Dict] = []
        
        # Function availability
        self.dsk_functions_available = False
    
    def get_param_files(self) -> Dict:
        """Get list of available parameter files."""
        param_dir = "../param"
        if not os.path.exists(param_dir):
            raise FileNotFoundError("Parameter directory not found")
        
        param_files = []
        for file_path in glob.glob(os.path.join(param_dir, "*.param")):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            param_files.append({
                "name": file_name,
                "path": file_path,
                "size": file_size
            })
        
        param_files.sort(key=lambda x: x["name"])
        
        return {
            "param_files": param_files,
            "current": self.current_param_file
        }
    
    def validate_param_file(self, param_file: str) -> str:
        """Validate parameter file exists and return full path."""
        full_path = os.path.join("../param", param_file)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Parameter file not found: {param_file}")
        return full_path
    
    def set_initialized(self, param_file: str, trace_key: Dict):
        """Mark system as initialized with given parameters."""
        self.system_initialized = True
        self.current_param_file = param_file
        self.trace_key = trace_key
    
    def ensure_initialized(self):
        """Ensure the system is initialized before operations."""
        if not self.system_initialized:
            raise Exception("System not initialized. Please run setup first.")
    
    def reset(self):
        """Reset all system state."""
        self.key_list.clear()
        self.address_list.clear()
        self.dsk_list.clear()
        self.tx_message_list.clear()
        self.trace_key = None
        self.system_initialized = False
        self.current_param_file = None
    
    def get_status(self) -> Dict:
        """Get current system status."""
        return {
            "initialized": self.system_initialized,
            "param_file": self.current_param_file,
            "trace_key_set": self.trace_key is not None,
            "keys_count": len(self.key_list),
            "addresses_count": len(self.address_list),
            "dsks_count": len(self.dsk_list),
            "tx_messages_count": len(self.tx_message_list),
            "dsk_functions_available": self.dsk_functions_available,
            "architecture": "interactive_selectable_inputs"
        }


# Global configuration instance
config = SteuthConfig()