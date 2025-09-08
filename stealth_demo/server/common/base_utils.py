"""
Base utility functions shared across all cryptographic schemes.
These functions have identical implementation in both stealth and sitaiba.
"""
from ctypes import create_string_buffer
from typing import List


def validate_index(index: int, data_list: list, item_name: str):
    """
    Validate index against list bounds.
    
    Args:
        index: The index to validate
        data_list: The list to check against
        item_name: Name of the item for error messages
        
    Raises:
        ValueError: If index is out of bounds
    """
    if index < 0 or index >= len(data_list):
        raise ValueError(f"Invalid {item_name}: {index} (valid range: 0-{len(data_list)-1})")


def hex_to_bytes_safe(hex_str: str) -> bytes:
    """
    Safely convert hex string to bytes with validation.
    Combines the best practices from both scheme implementations.
    
    Args:
        hex_str: Hexadecimal string to convert
        
    Returns:
        bytes: The converted bytes
        
    Raises:
        ValueError: If hex string is invalid
    """
    if not hex_str:
        raise ValueError("Empty hex string")
    
    try:
        # Ensure even length by padding with leading zero if needed (sitaiba logic)
        if len(hex_str) % 2 != 0:
            hex_str = '0' + hex_str
        return bytes.fromhex(hex_str)
    except ValueError as e:
        raise ValueError(f"Invalid hex string '{hex_str}': {str(e)}")


def create_buffer(size: int):
    """
    Create a string buffer with proper initialization.
    
    Args:
        size: Buffer size in bytes
        
    Returns:
        ctypes buffer: Initialized buffer
    """
    buf = create_string_buffer(size)
    # Initialize to zero (stealth implementation)
    for i in range(size):
        buf[i] = 0
    return buf


def create_multiple_buffers(count: int, size: int) -> List:
    """
    Create multiple string buffers of the same size.
    
    Args:
        count: Number of buffers to create
        size: Size of each buffer
        
    Returns:
        List of initialized buffers
    """
    return [create_buffer(size) for _ in range(count)]