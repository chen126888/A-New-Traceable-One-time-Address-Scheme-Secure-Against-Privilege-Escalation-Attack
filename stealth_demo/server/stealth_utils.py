"""
Utility functions for Stealth scheme.
Handles hex/bytes conversion, buffer management, and common operations.
"""
from ctypes import create_string_buffer
from typing import Optional
from stealth_library_wrapper import get_stealth_library


def get_stealth_element_size() -> int:
    """Get element sizes for buffer allocation."""
    try:
        stealth_lib = get_stealth_library()
        if not stealth_lib.is_initialized():
            return 512
        g1_size = stealth_lib.get_element_size_G1()
        zr_size = stealth_lib.get_element_size_Zr()
        return max(g1_size, zr_size, 512)
    except:
        return 512


def bytes_to_hex_safe_fixed_stealth(buf, element_type: str = 'G1') -> str:
    """Convert buffer to hex string with fixed size for Stealth."""
    try:
        stealth_lib = get_stealth_library()
        if element_type == 'G1':
            expected_size = stealth_lib.get_element_size_G1()
        elif element_type == 'Zr':
            expected_size = stealth_lib.get_element_size_Zr()
        else:
            raise ValueError(f"Unknown element type: {element_type}")
    except:
        # Fallback if library not available
        expected_size = 512
    
    if hasattr(buf, 'raw'):
        data = buf.raw[:expected_size] if expected_size <= len(buf.raw) else buf.raw
    else:
        data = buf[:expected_size] if expected_size <= len(buf) else buf
    
    # Check for truly empty data
    if len(data) == 0:
        return ""
    
    return data.hex()


def hex_to_bytes_safe_stealth(hex_str: str) -> bytes:
    """Safely convert hex string to bytes."""
    try:
        if len(hex_str) % 2 != 0:
            raise ValueError("Hex string length must be even")
        return bytes.fromhex(hex_str)
    except ValueError as e:
        print(f"Error converting hex to bytes: {e}")
        return b""


def create_buffer_stealth(size: Optional[int] = None) -> create_string_buffer:
    """Create a buffer for Stealth operations."""
    if size is None:
        size = get_stealth_element_size()
    return create_string_buffer(size)


def validate_stealth_hex(hex_str: str) -> bool:
    """Validate if hex string is properly formatted."""
    if not hex_str:
        return False
    if len(hex_str) % 2 != 0:
        return False
    try:
        bytes.fromhex(hex_str)
        return True
    except ValueError:
        return False


def stealth_bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string."""
    return data.hex()


def stealth_hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex string to bytes with validation."""
    if not validate_stealth_hex(hex_str):
        raise ValueError("Invalid hex string format")
    return bytes.fromhex(hex_str)


def trim_stealth_buffer(buf) -> bytes:
    """Trim buffer to actual data size."""
    if hasattr(buf, 'raw'):
        data = buf.raw
    else:
        data = buf
    
    # Find the first occurrence of null bytes and trim there
    null_pos = data.find(b'\x00')
    if null_pos == -1:
        return data
    elif null_pos == 0:
        # If starts with null, find first non-null
        for i, byte in enumerate(data):
            if byte != 0:
                return data[i:]
        return b""  # All null
    else:
        return data[:null_pos]


def format_stealth_key_display(key_data: bytes, key_name: str) -> dict:
    """Format key data for display purposes."""
    return {
        "name": key_name,
        "hex": key_data.hex(),
        "size": len(key_data),
        "preview": key_data.hex()[:32] + "..." if len(key_data.hex()) > 32 else key_data.hex()
    }


def format_stealth_signature_display(q_sigma: bytes, h: bytes) -> dict:
    """Format signature components for display."""
    return {
        "q_sigma": {
            "hex": q_sigma.hex(),
            "size": len(q_sigma),
            "preview": q_sigma.hex()[:32] + "..." if len(q_sigma.hex()) > 32 else q_sigma.hex()
        },
        "h": {
            "hex": h.hex(), 
            "size": len(h),
            "preview": h.hex()[:32] + "..." if len(h.hex()) > 32 else h.hex()
        }
    }


def verify_stealth_library_available() -> bool:
    """Check if Stealth library is available and initialized."""
    try:
        stealth_lib = get_stealth_library()
        return stealth_lib.is_initialized()
    except:
        return False


def initialize_stealth_library(param_file: str) -> bool:
    """Initialize Stealth library with parameter file."""
    try:
        stealth_lib = get_stealth_library()
        return stealth_lib.init(param_file)
    except Exception as e:
        print(f"Failed to initialize Stealth library: {e}")
        return False


def get_stealth_performance_info(iterations: int = 100) -> dict:
    """Get performance information from Stealth library."""
    try:
        stealth_lib = get_stealth_library()
        if not stealth_lib.is_initialized():
            return {}
        
        return stealth_lib.performance_test(iterations)
    except Exception as e:
        print(f"Error getting performance info: {e}")
        return {}


def cleanup_stealth_library():
    """Cleanup Stealth library resources."""
    try:
        stealth_lib = get_stealth_library()
        stealth_lib.cleanup()
    except:
        pass


def reset_stealth_performance():
    """Reset Stealth performance counters."""
    try:
        stealth_lib = get_stealth_library()
        stealth_lib.reset_performance()
    except:
        pass