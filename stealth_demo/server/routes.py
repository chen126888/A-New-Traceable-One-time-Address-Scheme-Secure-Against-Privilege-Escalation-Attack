"""
API routes for the stealth demo application.
Contains all Flask routes organized by functionality.
"""
from flask import request, jsonify
from config import config
from crypto_services import CryptoServices


def setup_routes(app):
    """Setup all API routes for the Flask app."""
    
    @app.route("/param_files", methods=["GET"])
    def get_param_files():
        """Get list of available parameter files"""
        try:
            return jsonify(config.get_param_files())
        except Exception as e:
            raise e

    @app.route("/setup", methods=["POST"])
    def setup():
        """Initialize the system with selected parameter file"""
        try:
            data = request.get_json()
            if not data or 'param_file' not in data:
                return jsonify({"error": "Please specify param_file"}), 400
            
            param_file = data['param_file']
            result = CryptoServices.setup_system(param_file)
            return jsonify(result)
            
        except Exception as e:
            config.system_initialized = False
            config.current_param_file = None
            raise e

    @app.route("/keygen", methods=["GET"])
    def keygen():
        """Generate a new key pair"""
        try:
            result = CryptoServices.generate_keypair()
            return jsonify(result)
        except Exception as e:
            raise e

    @app.route("/keylist", methods=["GET"])
    def keylist():
        """Get list of all generated keys"""
        return jsonify(config.key_list)

    @app.route("/addrgen", methods=["POST"])
    def addrgen():
        """Generate address with selected key"""
        try:
            data = request.get_json()
            if not data or 'key_index' not in data:
                return jsonify({"error": "Please specify key_index"}), 400
            
            key_index = data['key_index']
            result = CryptoServices.generate_address(key_index)
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/addresslist", methods=["GET"])
    def addresslist():
        """Get list of all generated addresses"""
        return jsonify(config.address_list)

    @app.route("/verify_addr", methods=["POST"])
    def verify_addr():
        """Verify address with selected key"""
        try:
            data = request.get_json()
            if not data or 'address_index' not in data or 'key_index' not in data:
                return jsonify({"error": "Please specify address_index and key_index"}), 400
            
            addr_index = data['address_index']
            key_index = data['key_index']
            result = CryptoServices.verify_address(addr_index, key_index)
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/dskgen", methods=["POST"])
    def dskgen():
        """Generate DSK for selected address and key"""
        try:
            data = request.get_json()
            if not data or 'address_index' not in data or 'key_index' not in data:
                return jsonify({"error": "Please specify address_index and key_index"}), 400
            
            addr_index = data['address_index']
            key_index = data['key_index']
            result = CryptoServices.generate_dsk(addr_index, key_index)
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/dsklist", methods=["GET"])
    def dsklist():
        """Get list of all generated DSKs"""
        return jsonify(config.dsk_list)

    @app.route("/sign", methods=["POST"])
    def sign_message():
        """Sign message with selected DSK or key"""
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({"error": "Please specify message"}), 400
            
            message = data['message']
            dsk_index = data.get('dsk_index')
            address_index = data.get('address_index')
            key_index = data.get('key_index')
            
            if dsk_index is not None:
                result = CryptoServices.sign_message(message, dsk_index=dsk_index)
            elif address_index is not None and key_index is not None:
                result = CryptoServices.sign_message(message, address_index=address_index, key_index=key_index)
            else:
                return jsonify({"error": "Please specify either dsk_index or (address_index and key_index)"}), 400
            
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/verify_signature", methods=["POST"])
    def verify_signature():
        """Verify signature"""
        try:
            data = request.get_json()
            required_fields = ['message', 'q_sigma_hex', 'h_hex', 'address_index']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing {field}"}), 400
            
            result = CryptoServices.verify_signature(
                data['message'], 
                data['q_sigma_hex'], 
                data['h_hex'], 
                data['address_index']
            )
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/trace", methods=["POST"])
    def trace_identity():
        """Trace identity for selected address"""
        try:
            data = request.get_json()
            if not data or 'address_index' not in data:
                return jsonify({"error": "Please specify address_index"}), 400
            
            addr_index = data['address_index']
            result = CryptoServices.trace_identity(addr_index)
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/performance_test", methods=["POST"])
    def performance_test():
        """Run performance test using C library"""
        try:
            data = request.get_json()
            iterations = data.get('iterations', 100) if data else 100
            result = CryptoServices.performance_test(iterations)
            return jsonify(result)
        except Exception as e:
            raise e

    @app.route("/status", methods=["GET"])
    def status():
        """Get system status"""
        from library_wrapper import stealth_lib
        
        status_data = config.get_status()
        
        # Add library-specific information
        try:
            if config.system_initialized:
                g1_size, zr_size = stealth_lib.get_element_sizes()
                status_data.update({
                    "g1_element_size": g1_size,
                    "zr_element_size": zr_size
                })
        except:
            pass
        
        status_data["library_loaded"] = True
        return jsonify(status_data)

    @app.route("/reset", methods=["POST"])
    def reset_system():
        """Reset the system state"""
        try:
            from library_wrapper import stealth_lib
            
            if config.system_initialized:
                stealth_lib.reset_performance()
            
            config.reset()
            
            print("🧹 All backend data cleared")
            
            return jsonify({
                "status": "reset complete",
                "message": "All system state has been reset",
                "keys_count": len(config.key_list),
                "addresses_count": len(config.address_list)
            })
        except Exception as e:
            raise e

    @app.route("/tx_messages", methods=["GET"])
    def get_tx_messages():
        """Get list of all transaction messages"""
        return jsonify(config.tx_message_list)