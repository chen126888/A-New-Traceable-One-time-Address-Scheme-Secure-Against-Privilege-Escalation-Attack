"""
HDWSA Utility Functions

This module provides utility functions for HDWSA operations including
hierarchical ID management, buffer handling, and data conversion.
"""

import ctypes
from typing import List, Dict, Any, Optional
from .hdwsa_wrapper import get_library


def get_element_sizes():
    """Get element sizes for G1, Zr, and GT groups."""
    hdwsa_lib = get_library()
    
    g1_size = hdwsa_lib.hdwsa_element_size_G1_simple()
    zr_size = hdwsa_lib.hdwsa_element_size_Zr_simple()
    gt_size = hdwsa_lib.hdwsa_element_size_GT_simple()
    
    if g1_size <= 0 or zr_size <= 0 or gt_size <= 0:
        raise Exception("Failed to get element sizes - library not initialized")
    
    return g1_size, zr_size, gt_size


def create_buffer(size: int):
    """Create a ctypes buffer of specified size."""
    return ctypes.create_string_buffer(size)


def bytes_to_hex_safe_fixed(buffer, element_type: str) -> Optional[str]:
    """Convert bytes buffer to hex string with type validation."""
    try:
        g1_size, zr_size, gt_size = get_element_sizes()
        
        # Determine expected size based on element type
        if element_type == 'G1':
            expected_size = g1_size
        elif element_type == 'Zr':
            expected_size = zr_size
        elif element_type == 'GT':
            expected_size = gt_size
        else:
            raise ValueError(f"Unknown element type: {element_type}")
        
        # Convert buffer to bytes
        if hasattr(buffer, 'raw'):
            data = buffer.raw[:expected_size]
        else:
            data = bytes(buffer)[:expected_size]
        
        # Check for all-zero data (likely uninitialized)
        if all(b == 0 for b in data):
            return None
        
        return data.hex()
        
    except Exception as e:
        print(f"Error converting {element_type} to hex: {e}")
        return None


def hex_to_buffer(hex_string: str, element_type: str):
    """Convert hex string to ctypes buffer."""
    if not hex_string:
        raise ValueError("Hex string cannot be empty")
    
    try:
        data = bytes.fromhex(hex_string)
        buffer = ctypes.create_string_buffer(data)
        return buffer
    except ValueError as e:
        raise ValueError(f"Invalid hex string for {element_type}: {e}")


def generate_hierarchical_id(parent_id: str, child_index: int) -> str:
    """Generate hierarchical ID for child wallet."""
    if not parent_id:
        # Root level
        return f"id_{child_index}"
    else:
        # Child level
        return f"{parent_id},id_{child_index}"


def parse_hierarchical_id(full_id: str) -> List[int]:
    """Parse hierarchical ID to list of indices."""
    if not full_id:
        return []
    
    parts = full_id.split(',')
    indices = []
    
    for part in parts:
        if part.startswith('id_'):
            try:
                index = int(part[3:])  # Remove 'id_' prefix
                indices.append(index)
            except ValueError:
                raise ValueError(f"Invalid ID format: {part}")
        else:
            raise ValueError(f"Invalid ID part: {part}")
    
    return indices


def get_wallet_level(full_id: str) -> int:
    """Get the level of wallet in hierarchy (0 = root, 1 = first level, etc.)."""
    if not full_id:
        return 0
    return len(full_id.split(','))


def get_parent_id(full_id: str) -> Optional[str]:
    """Get parent ID from hierarchical ID."""
    if not full_id or ',' not in full_id:
        return None
    
    parts = full_id.split(',')
    return ','.join(parts[:-1])


def generate_wallet_tree(wallets: List[Dict]) -> Dict:
    """Generate hierarchical wallet tree structure."""
    tree = {"children": {}}
    
    for wallet in wallets:
        full_id = wallet.get('full_id', '')
        if not full_id:
            continue
        
        # Navigate to the correct position in tree
        current = tree
        parts = full_id.split(',')
        
        for i, part in enumerate(parts):
            if part not in current["children"]:
                current["children"][part] = {
                    "children": {},
                    "wallet": None
                }
            
            # If this is the last part, set the wallet data
            if i == len(parts) - 1:
                current["children"][part]["wallet"] = wallet
            
            current = current["children"][part]
    
    return tree


def validate_index(index: int, items_list: List, name: str = "index"):
    """Validate that index is within bounds of items list."""
    if not isinstance(index, int):
        raise TypeError(f"{name} must be an integer")
    
    if index < 0:
        raise ValueError(f"{name} must be non-negative")
    
    if index >= len(items_list):
        raise ValueError(f"{name} {index} out of range (0-{len(items_list)-1})")


def create_performance_summary(operations_count: int) -> Dict[str, Any]:
    """Create performance summary from HDWSA library statistics."""
    hdwsa_lib = get_library()
    
    # Get performance string from library
    buffer_size = 1024
    buffer = ctypes.create_string_buffer(buffer_size)
    
    result = hdwsa_lib.hdwsa_get_performance_string_simple(buffer, buffer_size)
    
    if result != 0:
        return {
            "error": "Failed to get performance statistics",
            "operations_count": operations_count
        }
    
    performance_text = buffer.value.decode('utf-8')
    
    return {
        "status": "completed",
        "operations_count": operations_count,
        "success_rate": 100.0,
        "successful_operations": operations_count,
        "performance_details": performance_text
    }


def reset_performance_stats():
    """Reset performance statistics in HDWSA library."""
    hdwsa_lib = get_library()
    hdwsa_lib.hdwsa_reset_performance_simple()
    return True


def format_wallet_info(wallet: Dict) -> Dict[str, Any]:
    """Format wallet information for API response."""
    return {
        "index": wallet.get("index", 0),
        "full_id": wallet.get("full_id", ""),
        "level": get_wallet_level(wallet.get("full_id", "")),
        "parent_id": get_parent_id(wallet.get("full_id", "")),
        "A_hex": wallet.get("A_hex", "")[:64] + "..." if wallet.get("A_hex") else "",
        "B_hex": wallet.get("B_hex", "")[:64] + "..." if wallet.get("B_hex") else "",
        "param_file": wallet.get("param_file", ""),
        "status": wallet.get("status", "unknown")
    }