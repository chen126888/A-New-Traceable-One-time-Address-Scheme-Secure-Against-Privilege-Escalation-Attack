"""
HDWSA Services

This module provides the main service class for HDWSA operations.
It implements the business logic layer that integrates with the 
multi-scheme configuration system.
"""

from typing import Dict, Any, List, Optional
from multi_scheme_config import config
from .hdwsa_wrapper import get_library, initialize_library, cleanup_library
from .hdwsa_utils import (
    get_element_sizes, create_buffer, bytes_to_hex_safe_fixed, hex_to_buffer,
    generate_hierarchical_id, validate_index, create_performance_summary,
    reset_performance_stats, generate_wallet_tree, format_wallet_info
)


class HdwsaServices:
    """HDWSA cryptographic service implementation."""
    
    def __init__(self):
        """Initialize HDWSA services."""
        self.scheme_name = "hdwsa"
    
    @staticmethod
    def setup_system(param_file: str) -> Dict[str, Any]:
        """Initialize HDWSA system with parameter file."""
        try:
            # Initialize library
            initialize_library()
            hdwsa_lib = get_library()
            
            # Validate parameter file
            full_path = config.validate_param_file(param_file)
            
            # Initialize HDWSA library
            result = hdwsa_lib.hdwsa_init_simple(full_path.encode('utf-8'))
            if result != 0:
                raise Exception(f"Failed to initialize HDWSA with {param_file}")
            
            # Get element sizes
            g1_size, zr_size, gt_size = get_element_sizes()
            
            # Generate root wallet keys
            root_A_buf = create_buffer(g1_size)
            root_B_buf = create_buffer(g1_size)
            root_alpha_buf = create_buffer(zr_size)
            root_beta_buf = create_buffer(zr_size)
            
            result = hdwsa_lib.hdwsa_root_keygen_simple(
                root_A_buf, root_B_buf, root_alpha_buf, root_beta_buf
            )
            
            if result != 0:
                raise Exception("Failed to generate root wallet keys")
            
            # Convert to hex
            root_A_hex = bytes_to_hex_safe_fixed(root_A_buf, 'G1')
            root_B_hex = bytes_to_hex_safe_fixed(root_B_buf, 'G1')
            root_alpha_hex = bytes_to_hex_safe_fixed(root_alpha_buf, 'Zr')
            root_beta_hex = bytes_to_hex_safe_fixed(root_beta_buf, 'Zr')
            
            if not all([root_A_hex, root_B_hex, root_alpha_hex, root_beta_hex]):
                raise Exception("Failed to convert root keys to hex")
            
            # Create root wallet info for storage
            root_wallet = {
                "A_hex": root_A_hex,
                "B_hex": root_B_hex,
                "alpha_hex": root_alpha_hex,
                "beta_hex": root_beta_hex
            }
            
            # Update configuration
            config.set_initialized(param_file, root_wallet, "hdwsa")
            
            return {
                "status": "setup complete",
                "message": f"HDWSA system initialized with {param_file}",
                "scheme": "hdwsa",
                "param_file": param_file,
                "system_initialized": True,
                "root_A_hex": root_A_hex,
                "root_B_hex": root_B_hex,
                "root_alpha_hex": root_alpha_hex,
                "root_beta_hex": root_beta_hex,
                "g1_size": g1_size,
                "zr_size": zr_size,
                "gt_size": gt_size,
                "hierarchical_wallets": True,
                "dsk_functions_available": True
            }
            
        except Exception as e:
            # Reset configuration on error
            config.reset_scheme("hdwsa")
            raise e
    
    @staticmethod
    def generate_keypair() -> Dict[str, Any]:
        """Generate a new hierarchical wallet keypair."""
        config.ensure_initialized("hdwsa")
        
        # Determine the next wallet index and ID
        current_wallets = config.key_list
        next_index = len(current_wallets)
        
        # For now, generate root-level wallets (id_0, id_1, etc.)
        # In a full implementation, this could be extended to support child wallets
        wallet_id = f"id_{next_index}"
        
        # Get element sizes
        g1_size, zr_size, gt_size = get_element_sizes()
        
        # Get root keys from trace_key (stored during setup)
        root_wallet = config.trace_key
        if not root_wallet:
            raise Exception("Root wallet not found - system may not be properly initialized")
        
        # Create buffers for root keys
        root_A_buf = hex_to_buffer(root_wallet['A_hex'], 'G1')
        root_B_buf = hex_to_buffer(root_wallet['B_hex'], 'G1')
        root_alpha_buf = hex_to_buffer(root_wallet['alpha_hex'], 'Zr')
        root_beta_buf = hex_to_buffer(root_wallet['beta_hex'], 'Zr')
        
        # Create buffers for user keys
        user_A_buf = create_buffer(g1_size)
        user_B_buf = create_buffer(g1_size)
        user_alpha_buf = create_buffer(zr_size)
        user_beta_buf = create_buffer(zr_size)
        
        hdwsa_lib = get_library()
        result = hdwsa_lib.hdwsa_keypair_gen_simple(
            user_A_buf, user_B_buf, user_alpha_buf, user_beta_buf,
            root_alpha_buf, root_beta_buf, wallet_id.encode('utf-8')
        )
        
        if result != 0:
            raise Exception(f"Failed to generate keypair for wallet {wallet_id}")
        
        # Convert to hex
        A_hex = bytes_to_hex_safe_fixed(user_A_buf, 'G1')
        B_hex = bytes_to_hex_safe_fixed(user_B_buf, 'G1')
        alpha_hex = bytes_to_hex_safe_fixed(user_alpha_buf, 'Zr')
        beta_hex = bytes_to_hex_safe_fixed(user_beta_buf, 'Zr')
        
        if not all([A_hex, B_hex, alpha_hex, beta_hex]):
            raise Exception("Failed to convert user keys to hex")
        
        # Create wallet item
        wallet_item = {
            "index": next_index,
            "full_id": wallet_id,
            "A_hex": A_hex,
            "B_hex": B_hex,
            "alpha_hex": alpha_hex,
            "beta_hex": beta_hex,
            "param_file": config.current_param_file,
            "status": "generated"
        }
        
        config.key_list.append(wallet_item)
        return wallet_item
    
    @staticmethod
    def generate_address(key_index: int) -> Dict[str, Any]:
        """Generate address from specified wallet."""
        config.ensure_initialized("hdwsa")
        validate_index(key_index, config.key_list, "key_index")
        
        wallet = config.key_list[key_index]
        
        # Get element sizes
        g1_size, zr_size, gt_size = get_element_sizes()
        
        # Create buffers for wallet keys
        A_buf = hex_to_buffer(wallet['A_hex'], 'G1')
        B_buf = hex_to_buffer(wallet['B_hex'], 'G1')
        
        # Create buffers for address
        Qr_buf = create_buffer(g1_size)
        Qvk_buf = create_buffer(gt_size)
        
        hdwsa_lib = get_library()
        result = hdwsa_lib.hdwsa_addr_gen_simple(Qr_buf, Qvk_buf, A_buf, B_buf)
        
        if result != 0:
            raise Exception("Failed to generate address")
        
        # Convert to hex
        Qr_hex = bytes_to_hex_safe_fixed(Qr_buf, 'G1')
        Qvk_hex = bytes_to_hex_safe_fixed(Qvk_buf, 'GT')
        
        if not all([Qr_hex, Qvk_hex]):
            raise Exception("Failed to convert address to hex")
        
        # Create address item
        address_index = len(config.address_list)
        address_item = {
            "index": address_index,
            "key_index": key_index,
            "wallet_id": wallet['full_id'],
            "Qr_hex": Qr_hex,
            "Qvk_hex": Qvk_hex,
            "param_file": config.current_param_file,
            "status": "generated"
        }
        
        config.address_list.append(address_item)
        return address_item
    
    @staticmethod
    def recognize_address(address_index: int, key_index: int, fast: bool = True) -> Dict[str, Any]:
        """Recognize if address belongs to specified wallet."""
        config.ensure_initialized("hdwsa")
        validate_index(address_index, config.address_list, "address_index")
        validate_index(key_index, config.key_list, "key_index")
        
        address = config.address_list[address_index]
        wallet = config.key_list[key_index]
        
        # Convert address and wallet data to buffers
        Qr_buf = hex_to_buffer(address['Qr_hex'], 'G1')
        Qvk_buf = hex_to_buffer(address['Qvk_hex'], 'GT')
        A_buf = hex_to_buffer(wallet['A_hex'], 'G1')
        B_buf = hex_to_buffer(wallet['B_hex'], 'G1')
        beta_buf = hex_to_buffer(wallet['beta_hex'], 'Zr')  # Add missing beta parameter
        
        hdwsa_lib = get_library()
        
        # HDWSA address recognition (no method parameter needed)
        result = hdwsa_lib.hdwsa_addr_recognize_simple(Qvk_buf, Qr_buf, A_buf, B_buf, beta_buf)
        method = "fast" if fast else "full"  # Keep for API compatibility, but HDWSA only has one method
        
        is_match = (result == 1)  # 1 = match, 0 = no match, -1 = error
        
        if result == -1:
            raise Exception("Address recognition failed")
        
        return {
            "address_index": address_index,
            "key_index": key_index,
            "wallet_id": wallet['full_id'],
            "is_match": is_match,
            "method": method,
            "status": "verified" if is_match else "no_match"
        }
    
    @staticmethod
    def generate_dsk(address_index: int, key_index: int) -> Dict[str, Any]:
        """Generate Derived Signing Key (DSK)."""
        config.ensure_initialized("hdwsa")
        validate_index(address_index, config.address_list, "address_index")
        validate_index(key_index, config.key_list, "key_index")
        
        address = config.address_list[address_index]
        wallet = config.key_list[key_index]
        
        # Get element sizes
        g1_size, zr_size, gt_size = get_element_sizes()
        
        # Convert necessary components to buffers
        Qr_buf = hex_to_buffer(address['Qr_hex'], 'G1')
        B_buf = hex_to_buffer(wallet['B_hex'], 'G1')
        alpha_buf = hex_to_buffer(wallet['alpha_hex'], 'Zr')
        beta_buf = hex_to_buffer(wallet['beta_hex'], 'Zr')
        
        # Create DSK buffer
        dsk_buf = create_buffer(g1_size)
        
        hdwsa_lib = get_library()
        # Corrected call: dsk_gen(dsk, Qr, B, alpha, beta)
        result = hdwsa_lib.hdwsa_dsk_gen_simple(dsk_buf, Qr_buf, B_buf, alpha_buf, beta_buf)
        
        if result != 0:
            raise Exception("Failed to generate DSK")
        
        # Convert to hex
        dsk_hex = bytes_to_hex_safe_fixed(dsk_buf, 'G1')
        
        if not dsk_hex:
            raise Exception("Failed to convert DSK to hex")
        
        # Create DSK item
        dsk_index = len(config.dsk_list)
        dsk_item = {
            "index": dsk_index,
            "address_index": address_index,
            "key_index": key_index,
            "wallet_id": wallet['full_id'],
            "dsk_hex": dsk_hex,
            "param_file": config.current_param_file,
            "status": "generated"
        }
        
        config.dsk_list.append(dsk_item)
        return dsk_item
    
    @staticmethod
    def sign_message(message: str, dsk_index: int = None, address_index: int = None, key_index: int = None) -> Dict:
        """Sign message using HDWSA DSK."""
        config.ensure_initialized("hdwsa")
        
        if dsk_index is None:
            raise ValueError("dsk_index is required for HDWSA message signing")
        
        validate_index(dsk_index, config.dsk_list, "dsk_index")
        
        dsk_item = config.dsk_list[dsk_index]
        address_index = dsk_item['address_index']
        address = config.address_list[address_index]
        
        # Convert to buffers
        dsk_buf = hex_to_buffer(dsk_item['dsk_hex'], 'G1')
        Qr_buf = hex_to_buffer(address['Qr_hex'], 'G1')
        Qvk_buf = hex_to_buffer(address['Qvk_hex'], 'GT')
        
        # Create signature buffers
        g1_size, zr_size, gt_size = get_element_sizes()
        h_buf = create_buffer(zr_size)
        Q_sigma_buf = create_buffer(g1_size)
        
        hdwsa_lib = get_library()
        result = hdwsa_lib.hdwsa_sign_simple(h_buf, Q_sigma_buf, dsk_buf, Qr_buf, Qvk_buf, message.encode('utf-8'))
        
        if result != 0:
            raise Exception("Failed to sign message with HDWSA")
        
        h_hex = bytes_to_hex_safe_fixed(h_buf, 'Zr')
        Q_sigma_hex = bytes_to_hex_safe_fixed(Q_sigma_buf, 'G1')
        
        if not h_hex or not Q_sigma_hex:
            raise Exception("Failed to convert signature to hex")
        
        # Create signature item
        signature_index = len(config.tx_message_list)
        signature_item = {
            "index": signature_index,
            "id": f"sig_{signature_index}",
            "dsk_index": dsk_index,
            "address_index": address_index,
            "wallet_id": dsk_item['wallet_id'],
            "message": message,
            "h_hex": h_hex,
            "Q_sigma_hex": Q_sigma_hex,
            "param_file": config.current_param_file,
            "status": "signed"
        }
        
        # Add to transaction message list
        config.tx_message_list.append(signature_item)
        
        return signature_item
    
    @staticmethod
    def verify_signature(message: str, q_sigma_hex: str, h_hex: str, address_index: int) -> Dict:
        """Verify signature using HDWSA."""
        config.ensure_initialized("hdwsa")
        
        # Validate address index
        validate_index(address_index, config.address_list, "address_index")
        address = config.address_list[address_index]
        
        # Convert signature components to buffers
        h_buf = hex_to_buffer(h_hex, 'Zr')
        Q_sigma_buf = hex_to_buffer(q_sigma_hex, 'G1')
        Qr_buf = hex_to_buffer(address['Qr_hex'], 'G1')
        Qvk_buf = hex_to_buffer(address['Qvk_hex'], 'GT')
        
        hdwsa_lib = get_library()
        result = hdwsa_lib.hdwsa_verify_simple(h_buf, Q_sigma_buf, Qr_buf, Qvk_buf, message.encode('utf-8'))
        
        is_valid = (result == 1)  # 1 = valid, 0 = invalid, -1 = error
        
        if result == -1:
            raise Exception("Signature verification failed")
        
        return {
            "address_index": address_index,
            "wallet_id": address['wallet_id'],
            "message": message,
            "is_valid": is_valid,
            "status": "valid" if is_valid else "invalid",
            "h_hex": h_hex,
            "Q_sigma_hex": q_sigma_hex
        }
    
    @staticmethod
    def performance_test(iterations: int = 100) -> Dict[str, Any]:
        """Run HDWSA performance test using core library implementation."""
        config.ensure_initialized("hdwsa")
        
        try:
            # Reset performance statistics
            reset_performance_stats()
            
            # Run the core library performance test
            hdwsa_lib = get_library()
            successful_operations = hdwsa_lib.hdwsa_performance_test_simple(iterations)
            
            # Get performance summary from core library
            summary = create_performance_summary(iterations)
            summary.update({
                "iterations": iterations,
                "successful_operations": successful_operations,
                "success_rate": (successful_operations / iterations) * 100.0 if iterations > 0 else 0.0
            })
            
            return summary
            
        except Exception as e:
            return {
                "error": f"Performance test failed: {e}",
                "iterations": iterations,
                "successful_operations": 0,
                "success_rate": 0.0
            }
    
    @staticmethod
    def get_wallet_tree() -> Dict[str, Any]:
        """Get hierarchical wallet tree structure."""
        try:
            wallets = config.key_list
            tree = generate_wallet_tree(wallets)
            
            return {
                "scheme": "hdwsa",
                "wallet_tree": tree,
                "total_wallets": len(wallets),
                "status": "generated"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate wallet tree: {e}",
                "scheme": "hdwsa",
                "wallet_tree": {"children": {}},
                "total_wallets": 0,
                "status": "error"
            }