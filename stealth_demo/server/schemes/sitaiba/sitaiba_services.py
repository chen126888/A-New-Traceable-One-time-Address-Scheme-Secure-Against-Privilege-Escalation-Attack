"""
Cryptographic services module for SITAIBA operations.
Hangles key generation, address operations, DSK generation, recognition, and tracing.
Note: SITAIBA scheme does not support message signing/verification.
"""
from typing import Dict, Optional
from .sitaiba_wrapper import get_sitaiba_lib
from ...multi_scheme_config import config
from ...common.base_utils import hex_to_bytes_safe, validate_index
from ...common.scheme_utils import get_element_size, create_buffer, create_multiple_buffers, bytes_to_hex_safe_fixed, find_matching_key
from ...common.base_services import BaseSchemeService # Import the base class
from ctypes import c_double # For performance test results array


# Initialize SITAIBA lib when needed
def _get_lib():
    return get_sitaiba_lib()


class SitaibaServices(BaseSchemeService):
    """High-level SITAIBA cryptographic operations."""

    def __init__(self):
        self._scheme_name = 'sitaiba' # Set it before calling super().__init__()
        super().__init__()

    def _get_lib(self):
        return _get_lib()

    def _generate_tracer_key_with_param(self, param_file: str) -> Dict:
        sitaiba_lib = self._get_lib()
        g1_size, zr_size = sitaiba_lib.get_element_sizes()
        buf_size = max(g1_size, zr_size, 512)
        A_m_buf, a_m_buf = create_multiple_buffers(2, buf_size)

        sitaiba_lib.tracer_keygen(A_m_buf, a_m_buf, buf_size)

        A_m_hex = bytes_to_hex_safe_fixed(A_m_buf, 'G1')
        a_m_hex = bytes_to_hex_safe_fixed(a_m_buf, 'Zr')

        if not A_m_hex or not a_m_hex:
            raise Exception("Failed to generate SITAIBA tracer key")

        return {
            "TK_hex": A_m_hex,
            "k_hex": a_m_hex,
            "param_file": param_file,
            "status": "initialized"
        }

    def _call_c_keygen(self, A_buf, B_buf, a_buf, b_buf, buf_size: int):
        sitaiba_lib = self._get_lib()
        sitaiba_lib.keygen(A_buf, B_buf, a_buf, b_buf, buf_size)

    def _call_c_addr_gen(self, A_r_bytes, B_r_bytes, A_m_bytes, addr_buf, r1_buf, r2_buf, buf_size: int):
        sitaiba_lib = self._get_lib()
        sitaiba_lib.addr_gen(A_r_bytes, B_r_bytes, A_m_bytes, addr_buf, r1_buf, r2_buf, buf_size)

    def _call_c_recognize_address(self, address_data: Dict, key_data: Dict, fast: bool = True) -> bool:
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        r2_bytes = hex_to_bytes_safe(address_data['r2_hex'])
        A_r_bytes = hex_to_bytes_safe(key_data['A_hex'])
        a_r_bytes = hex_to_bytes_safe(key_data['a_hex'])

        sitaiba_lib = self._get_lib()

        if fast:
            result = sitaiba_lib.addr_recognize_fast(r1_bytes, r2_bytes, A_r_bytes, a_r_bytes)
        else:
            addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
            B_r_bytes = hex_to_bytes_safe(key_data['B_hex'])
            A_m_hex = config.trace_key['TK_hex']
            A_m_bytes = hex_to_bytes_safe(A_m_hex)
            result = sitaiba_lib.addr_recognize(addr_bytes, r1_bytes, r2_bytes,
                                              A_r_bytes, B_r_bytes, a_r_bytes, A_m_bytes)
        return result

    def _call_c_generate_dsk(self, address_data: Dict, key_data: Dict) -> Dict:
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        a_r_bytes = hex_to_bytes_safe(key_data['a_hex'])
        b_r_bytes = hex_to_bytes_safe(key_data['b_hex'])

        A_m_hex = config.trace_key['TK_hex']
        A_m_bytes = hex_to_bytes_safe(A_m_hex)

        buf_size = get_element_size()
        dsk_buf = create_buffer(buf_size)

        sitaiba_lib = self._get_lib()
        sitaiba_lib.onetime_skgen(r1_bytes, a_r_bytes, b_r_bytes, A_m_bytes, dsk_buf, buf_size)

        dsk_hex = bytes_to_hex_safe_fixed(dsk_buf, 'Zr')

        if not dsk_hex:
            raise Exception("Failed to generate SITAIBA DSK")

        return {
            "index": len(config.dsk_list),
            "id": f"dsk_{len(config.dsk_list)}",
            "dsk_hex": dsk_hex,
            "address_index": address_data['index'],
            "key_index": key_data['index'],
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "owner_A": key_data['A_hex'],
            "owner_B": key_data['B_hex'],
            "for_address": address_data['addr_hex'],
            "scheme": self._scheme_name,
            "status": "generated"
        }

    def _call_c_trace_identity(self, address_data: Dict) -> Dict:
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        r2_bytes = hex_to_bytes_safe(address_data['r2_hex'])

        a_m_hex = config.trace_key['k_hex']
        a_m_bytes = hex_to_bytes_safe(a_m_hex)

        buf_size = get_element_size()
        B_r_buf = create_buffer(buf_size)

        sitaiba_lib = self._get_lib()
        sitaiba_lib.trace(addr_bytes, r1_bytes, r2_bytes, a_m_bytes, B_r_buf, buf_size)

        B_recovered_hex = bytes_to_hex_safe_fixed(B_r_buf, 'G1')

        if not B_recovered_hex:
            raise Exception("Failed to trace SITAIBA identity")

        matched_key = find_matching_key(B_recovered_hex)

        return {
            "recovered_b_hex": B_recovered_hex,
            "matched_key": matched_key,
            "perfect_match": matched_key is not None,
        }

    def _call_c_performance_test(self, iterations: int) -> Dict:
        results = (c_double * 5)()
        sitaiba_lib = self._get_lib()
        sitaiba_lib.performance_test(iterations, results)
        return {
            "addr_gen_ms": round(results[0], 3),
            "addr_recognize_ms": round(results[1], 3),
            "fast_recognize_ms": round(results[2], 3),
            "onetime_sk_ms": round(results[3], 3),
            "trace_ms": round(results[4], 3),
        }

    # SITAIBA does not support signing/verification, so use base class's NotImplementedError
    # No need to override sign_message, verify_signature, sign_with_address_and_dsk
