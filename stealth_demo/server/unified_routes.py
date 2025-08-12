"""
Unified API routes for the multi-scheme cryptographic demo application.
Routes automatically dispatch to the current active scheme.
"""
from flask import request, jsonify
from multi_scheme_config import config
from scheme_manager import scheme_manager


def setup_routes(app):
    """Setup all API routes for the Flask app."""
    
    # Scheme management routes
    @app.route("/schemes", methods=["GET"])
    def get_schemes():
        """Get list of available schemes and current status"""
        try:
            return jsonify(scheme_manager.get_status())
        except Exception as e:
            raise e
    
    @app.route("/switch_scheme", methods=["POST"])
    def switch_scheme():
        """Switch to a different cryptographic scheme"""
        try:
            data = request.get_json()
            if not data or 'scheme' not in data:
                return jsonify({"error": "Please specify scheme name"}), 400
            
            scheme_name = data['scheme']
            result = scheme_manager.switch_scheme(scheme_name)
            
            # Update config to track current scheme
            config.set_current_scheme(scheme_name)
            
            return jsonify(result)
        except Exception as e:
            raise e
    
    @app.route("/scheme_capabilities", methods=["GET"])
    def get_scheme_capabilities():
        """Get capabilities of current or specified scheme"""
        try:
            scheme_name = request.args.get('scheme')
            capabilities = scheme_manager.get_scheme_capabilities(scheme_name)
            return jsonify(capabilities)
        except Exception as e:
            raise e
    
    # Parameter file management (shared across schemes)
    @app.route("/param_files", methods=["GET"])
    def get_param_files():
        """Get list of available parameter files"""
        try:
            return jsonify(config.get_param_files())
        except Exception as e:
            raise e
    
    # Core cryptographic operations (dispatched to current scheme)
    @app.route("/setup", methods=["POST"])
    def setup():
        """Initialize the current scheme with selected parameter file"""
        try:
            data = request.get_json()
            if not data or 'param_file' not in data:
                return jsonify({"error": "Please specify param_file"}), 400
            
            param_file = data['param_file']
            result = scheme_manager.setup_system(param_file)
            return jsonify(result)
            
        except Exception as e:
            # Reset scheme state on error
            config.reset_scheme()
            raise e

    @app.route("/keygen", methods=["GET"])
    def keygen():
        """Generate a new key pair using current scheme"""
        try:
            result = scheme_manager.generate_keypair()
            return jsonify(result)
        except Exception as e:
            raise e

    @app.route("/keylist", methods=["GET"])
    def keylist():
        """Get list of all generated keys for current scheme"""
        return jsonify({
            "keys": config.key_list,
            "scheme": config.current_scheme,
            "count": len(config.key_list)
        })

    @app.route("/addrgen", methods=["POST"])
    def addrgen():
        """Generate address with selected key using current scheme"""
        try:
            data = request.get_json()
            if not data or 'key_index' not in data:
                return jsonify({"error": "Please specify key_index"}), 400
            
            key_index = data['key_index']
            result = scheme_manager.generate_address(key_index)
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/addresslist", methods=["GET"])
    def addresslist():
        """Get list of all generated addresses for current scheme"""
        return jsonify({
            "addresses": config.address_list,
            "scheme": config.current_scheme,
            "count": len(config.address_list)
        })

    @app.route("/recognize_addr", methods=["POST"])
    def recognize_addr():
        """Recognize address with selected key using current scheme"""
        try:
            current_service = scheme_manager.get_current_service()
            if not hasattr(current_service, 'recognize_address'):
                return jsonify({"error": f"Address recognition not supported by {config.current_scheme}"}), 400
            
            data = request.get_json()
            if not data or 'address_index' not in data or 'key_index' not in data:
                return jsonify({"error": "Please specify address_index and key_index"}), 400
            
            addr_index = data['address_index']
            key_index = data['key_index']
            
            # Check if scheme supports fast/full recognition (SITAIBA)
            if config.current_scheme == 'sitaiba':
                fast = data.get('fast', True)  # Default to fast recognition
                result = current_service.recognize_address(addr_index, key_index, fast)
            else:
                # Stealth only has one recognition method
                result = current_service.recognize_address(addr_index, key_index)
            
            result["scheme"] = config.current_scheme
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/dskgen", methods=["POST"])
    def dskgen():
        """Generate DSK for selected address and key using current scheme"""
        try:
            data = request.get_json()
            if not data or 'address_index' not in data or 'key_index' not in data:
                return jsonify({"error": "Please specify address_index and key_index"}), 400
            
            addr_index = data['address_index']
            key_index = data['key_index']
            result = scheme_manager.generate_dsk(addr_index, key_index)
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/dsklist", methods=["GET"])
    def dsklist():
        """Get list of all generated DSKs for current scheme"""
        return jsonify({
            "dsks": config.dsk_list,
            "scheme": config.current_scheme,
            "count": len(config.dsk_list)
        })

    @app.route("/sign", methods=["POST"])
    def sign_message():
        """Sign message using current scheme (if supported)"""
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({"error": "Please specify message"}), 400
            
            result = scheme_manager.sign_message(
                data['message'],
                dsk_index=data.get('dsk_index'),
                address_index=data.get('address_index'),
                key_index=data.get('key_index')
            )
            
            # Check if signing is not supported
            if "error" in result and "doesn't support" in result["error"]:
                return jsonify(result), 400
            
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/sign_with_address_dsk", methods=["POST"])
    def sign_with_address_dsk():
        """Sign message using specific address and DSK - for testing correct/incorrect matches"""
        try:
            data = request.get_json()
            required_fields = ['message', 'address_index', 'dsk_index']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing {field}"}), 400
            
            # Use the current scheme service directly for this specific operation
            service = scheme_manager.get_current_service()
            
            # Call a new method that handles address + DSK signing
            result = service.sign_with_address_and_dsk(
                data['message'],
                data['address_index'], 
                data['dsk_index']
            )
            
            result["scheme"] = scheme_manager.get_current_scheme_name()
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/verify_signature", methods=["POST"])
    def verify_signature():
        """Verify signature using current scheme (if supported)"""
        try:
            data = request.get_json()
            required_fields = ['message', 'q_sigma_hex', 'h_hex', 'address_index']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing {field}"}), 400
            
            result = scheme_manager.verify_signature(
                data['message'], 
                data['q_sigma_hex'], 
                data['h_hex'], 
                data['address_index']
            )
            
            # Check if verification is not supported
            if "error" in result and "doesn't support" in result["error"]:
                return jsonify(result), 400
            
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/trace", methods=["POST"])
    def trace_identity():
        """Trace identity for selected address using current scheme"""
        try:
            data = request.get_json()
            if not data or 'address_index' not in data:
                return jsonify({"error": "Please specify address_index"}), 400
            
            addr_index = data['address_index']
            result = scheme_manager.trace_identity(addr_index)
            return jsonify(result)
            
        except Exception as e:
            raise e

    @app.route("/performance_test", methods=["POST"])
    def performance_test():
        """Run performance test using current scheme"""
        try:
            data = request.get_json()
            iterations = data.get('iterations', 100) if data else 100
            result = scheme_manager.performance_test(iterations)
            return jsonify(result)
        except Exception as e:
            raise e

    @app.route("/status", methods=["GET"])
    def status():
        """Get comprehensive system status"""
        try:
            # Get current scheme status
            scheme_status = config.get_status()
            
            # Get scheme manager status
            manager_status = scheme_manager.get_status()
            
            # Get overall config status
            all_status = config.get_all_status()
            
            return jsonify({
                "current_scheme_status": scheme_status,
                "scheme_manager_status": manager_status,
                "all_schemes_status": all_status,
                "library_loaded": True
            })
            
        except Exception as e:
            raise e

    @app.route("/reset", methods=["POST"])
    def reset_system():
        """Reset the current scheme or all schemes"""
        try:
            data = request.get_json() or {}
            reset_all = data.get('reset_all', False)
            
            if reset_all:
                config.reset_all_schemes()
                message = "All schemes have been reset"
            else:
                config.reset_scheme()
                message = f"Scheme '{config.current_scheme}' has been reset"
            
            print(f"🧹 {message}")
            
            return jsonify({
                "status": "reset complete",
                "message": message,
                "current_scheme": config.current_scheme,
                "keys_count": len(config.key_list),
                "addresses_count": len(config.address_list)
            })
        except Exception as e:
            raise e

    @app.route("/tx_messages", methods=["GET"])
    def get_tx_messages():
        """Get list of all transaction messages for current scheme (if supported)"""
        tx_messages = config.tx_message_list
        return jsonify({
            "tx_messages": tx_messages,
            "scheme": config.current_scheme,
            "count": len(tx_messages),
            "supported": len(tx_messages) > 0 or config.current_scheme == 'stealth'
        })