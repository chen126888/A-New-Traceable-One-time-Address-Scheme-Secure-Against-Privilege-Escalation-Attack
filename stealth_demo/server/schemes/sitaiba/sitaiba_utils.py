"""
SITAIBA-specific utility functions.
Inherits shared functionality and implements sitaiba-specific logic.
"""
from typing import Optional, Dict, Any
from .sitaiba_wrapper import get_sitaiba_lib
from ...multi_scheme_config import config
from ...common.scheme_utils import SchemeUtilsBase


class SitaibaUtils(SchemeUtilsBase):
    """SITAIBA-specific utility implementation."""

    def get_element_size(self) -> int:
        """Get maximum element size for buffer allocation (no initialization check)."""
        sitaiba_lib = get_sitaiba_lib()
        g1_size, zr_size = sitaiba_lib.get_element_sizes()
        return max(g1_size, zr_size, 512)  # Use larger buffer to be safe

    def bytes_to_hex_safe_fixed(self, buf, element_type: str = 'G1') -> str:
        """Convert buffer to hex string with SITAIBA-specific validation."""
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

    def find_matching_key(self, target_hex: str) -> Optional[Dict[str, Any]]:
        """Find key with matching B_hex value (SITAIBA-specific with partial matching)."""
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
