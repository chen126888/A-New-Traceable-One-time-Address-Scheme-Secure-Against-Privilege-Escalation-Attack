"""
Utility functions for the stealth demo application.
Handles hex/bytes conversion, buffer management, and common operations.
"""
from ctypes import create_string_buffer
from typing import Optional
from library_wrapper import stealth_lib
from config import config


def get_element_size() -> int:
    """Get element sizes for buffer allocation."""
    if not config.system_initialized:
        return 512
    g1_size, zr_size = stealth_lib.get_element_sizes()
    return max(g1_size, zr_size, 512)


def bytes_to_hex_safe_fixed(buf, element_type: str = 'G1') -> str:
    """Convert buffer to hex string with fixed size."""
    try:
        if element_type == 'G1':
            expected_size = stealth_lib.get_element_sizes()[0]
        elif element_type == 'Zr':
            expected_size = stealth_lib.get_element_sizes()[1]
        else:
            raise ValueError(f"Unknown element type: {element_type}")
    except:
        # Fallback if library not available
        expected_size = 512
    
    if expected_size > len(buf.raw):
        expected_size = len(buf.raw)
    
    data = buf.raw[:expected_size]
    
    if all(b == 0 for b in data):
        return ""
    
    return data.hex()


def hex_to_bytes_safe(hex_str: str) -> bytes:
    """Safely convert hex string to bytes."""
    try:
        if len(hex_str) % 2 != 0:
            raise ValueError("Hex string length must be even")
        return bytes.fromhex(hex_str)
    except ValueError as e:
        raise ValueError(f"Invalid hex string: {str(e)}")


def create_buffer(size: Optional[int] = None):
    """Create a string buffer with proper size."""
    if size is None:
        size = get_element_size()
    buf = create_string_buffer(size)
    # Initialize to zero
    for i in range(size):
        buf[i] = 0
    return buf


def create_multiple_buffers(count: int, size: Optional[int] = None):
    """Create multiple string buffers."""
    if size is None:
        size = get_element_size()
    return [create_buffer(size) for _ in range(count)]


def validate_index(index: int, data_list: list, item_name: str):
    """Validate index against list bounds."""
    if index < 0 or index >= len(data_list):
        raise ValueError(f"Invalid {item_name}: {index}")


def find_matching_key(target_b_hex: str):
    """Find key with matching B_hex value."""
    for i, key in enumerate(config.key_list):
        if key['B_hex'] == target_b_hex:
            return {
                "index": i,
                "id": key['id'],
                "match": True
            }
    return None