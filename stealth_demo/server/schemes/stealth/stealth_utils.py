"""
Stealth-specific utility functions.
Inherits shared functionality and implements stealth-specific logic.
"""
from typing import Optional, Dict, Any
from .stealth_wrapper import get_stealth_lib
from ...multi_scheme_config import config
from ...common.scheme_utils import SchemeUtilsBase


class StealthUtils(SchemeUtilsBase):
    """Stealth-specific utility implementation."""

    def get_element_size(self) -> int:
        """Get element sizes for buffer allocation with stealth-specific logic."""
        if not config.system_initialized:
            return 512
        stealth_lib = get_stealth_lib()
        g1_size, zr_size = stealth_lib.get_element_sizes()
        return max(g1_size, zr_size, 512)

    def bytes_to_hex_safe_fixed(self, buf, element_type: str = 'G1') -> str:
        """Convert buffer to hex string with stealth-specific logic."""
        try:
            stealth_lib = get_stealth_lib()
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

        # Stealth-specific: return empty string if all zeros
        if all(b == 0 for b in data):
            return ""

        return data.hex()

    def find_matching_key(self, target_b_hex: str) -> Optional[Dict[str, Any]]:
        """Find key with matching B_hex value (stealth-specific simple matching)."""
        for i, key in enumerate(config.key_list):
            if key['B_hex'] == target_b_hex:
                return {
                    "index": i,
                    "id": key['id'],
                    "match": True
                }
        return None
