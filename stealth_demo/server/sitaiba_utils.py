"""
Utility functions for SITAIBA scheme.
Handles hex/bytes conversion, buffer management, and common operations.
"""
from ctypes import create_string_buffer
from typing import Optional
from sitaiba_library_wrapper import sitaiba_lib


def get_sitaiba_element_size() -> int:
    """Get element sizes for buffer allocation."""
    if not sitaiba_lib.is_initialized():
        return 512
    g1_size, zr_size = sitaiba_lib.get_element_sizes()
    return max(g1_size, zr_size, 512)


def bytes_to_hex_safe_fixed_sitaiba(buf, element_type: str = 'G1') -> str:
    """Convert buffer to hex string with fixed size for SITAIBA."""
    try:
        if element_type == 'G1':
            expected_size = sitaiba_lib.get_element_sizes()[0]
        elif element_type == 'Zr':
            expected_size = sitaiba_lib.get_element_sizes()[1]
        else:
            raise ValueError(f"Unknown element type: {element_type}")
    except:
        # Fallback if library not available
        expected_size = 512
    
    if expected_size > len(buf.raw):
        expected_size = len(buf.raw)
    
    data = buf.raw[:expected_size]
    
    # Check for truly empty data (first few bytes are zero)
    # In cryptographic contexts, some elements might legitimately be all zeros
    if len(data) == 0:
        return ""
    
    return data.hex()


def hex_to_bytes_safe_sitaiba(hex_str: str) -> bytes:
    """Safely convert hex string to bytes."""
    try:
        if len(hex_str) % 2 != 0:
            raise ValueError("Hex string length must be even")
        return bytes.fromhex(hex_str)
    except ValueError as e:
        raise ValueError(f"Invalid hex string: {str(e)}")


def create_sitaiba_buffer(size: Optional[int] = None):
    """Create a string buffer with proper size for SITAIBA."""
    if size is None:
        size = get_sitaiba_element_size()
    buf = create_string_buffer(size)
    # Initialize to zero
    for i in range(size):
        buf[i] = 0
    return buf


def create_multiple_sitaiba_buffers(count: int, size: Optional[int] = None):
    """Create multiple string buffers for SITAIBA."""
    if size is None:
        size = get_sitaiba_element_size()
    return [create_sitaiba_buffer(size) for _ in range(count)]


def validate_sitaiba_index(index: int, data_list: list, item_name: str):
    """Validate index against list bounds."""
    if index < 0 or index >= len(data_list):
        raise ValueError(f"Invalid {item_name}: {index}")


def find_matching_sitaiba_key(target_b_hex: str, key_list: list):
    """Find key with matching B_hex value in SITAIBA key list."""
    for i, key in enumerate(key_list):
        if key['B_hex'] == target_b_hex:
            return {
                "index": i,
                "id": key['id'],
                "match": True
            }
    return None