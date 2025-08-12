"""
Utility functions for the SITAIBA scheme.
Buffer management, data conversion, and validation helpers.
"""
from ctypes import create_string_buffer
from typing import Optional
from .sitaiba_wrapper import get_sitaiba_lib
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from multi_scheme_config import config


def get_element_size() -> int:
    """Get maximum element size for buffer allocation."""
    sitaiba_lib = get_sitaiba_lib()
    g1_size, zr_size = sitaiba_lib.get_element_sizes()
    return max(g1_size, zr_size, 512)  # Use larger buffer to be safe


def bytes_to_hex_safe_fixed(buf, element_type: str = 'G1') -> str:
    """Convert buffer to hex string with validation."""
    if not buf:
        return ""
    
    try:
        # Get the appropriate element size
        sitaiba_lib = get_sitaiba_lib()
        g1_size, zr_size = sitaiba_lib.get_element_sizes()
        
        if element_type == 'G1':
            element_size = g1_size
        elif element_type == 'Zr':
            element_size = zr_size
        else:
            element_size = max(g1_size, zr_size)
        
        # Convert only the relevant bytes to hex string
        hex_str = buf.raw[:element_size].hex()
        
        return hex_str
    except Exception as e:
        print(f"Error converting buffer to hex: {e}")
        return ""


def hex_to_bytes_safe(hex_str: str) -> bytes:
    """Safely convert hex string to bytes with validation."""
    if not hex_str:
        raise ValueError("Empty hex string")
    
    try:
        # Ensure even length by padding with leading zero if needed
        if len(hex_str) % 2:
            hex_str = '0' + hex_str
        
        return bytes.fromhex(hex_str)
    except Exception as e:
        raise ValueError(f"Invalid hex string '{hex_str}': {e}")


def create_buffer(size: Optional[int] = None):
    """Create a string buffer with proper size."""
    if size is None:
        size = get_element_size()
    return create_string_buffer(size)


def create_multiple_buffers(count: int, size: Optional[int] = None):
    """Create multiple string buffers of the same size."""
    if size is None:
        size = get_element_size()
    
    buffers = []
    for _ in range(count):
        buffers.append(create_string_buffer(size))
    
    return buffers if count > 1 else buffers


def validate_index(index: int, data_list: list, item_name: str):
    """Validate index against list bounds."""
    if index < 0 or index >= len(data_list):
        raise ValueError(f"Invalid {item_name}: {index} (valid range: 0-{len(data_list)-1})")


def find_matching_key(target_hex: str):
    """Find key with matching B_hex value in the key list."""
    if not target_hex:
        return None
    
    # Search through all keys to find matching B_hex
    for key in config.key_list:
        if key.get('B_hex') == target_hex:
            return {
                "index": key['index'],
                "id": key['id'],
                "A_hex": key['A_hex'],
                "B_hex": key['B_hex'],
                "match_type": "perfect"
            }
    
    # If no perfect match, try partial matching (first 10 chars)
    target_prefix = target_hex[:10] if len(target_hex) >= 10 else target_hex
    for key in config.key_list:
        b_hex = key.get('B_hex', '')
        if b_hex.startswith(target_prefix):
            return {
                "index": key['index'],
                "id": key['id'],
                "A_hex": key['A_hex'],
                "B_hex": key['B_hex'],
                "match_type": "partial"
            }
    
    return None