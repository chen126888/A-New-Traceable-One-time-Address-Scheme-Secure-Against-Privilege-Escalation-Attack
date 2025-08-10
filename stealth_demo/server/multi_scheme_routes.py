"""
Multi-scheme API routes for the stealth demo application.
Supports multiple cryptographic schemes with dynamic switching.
"""
from flask import request, jsonify
from schemes.scheme_manager import scheme_manager
from schemes.stealth_scheme import StealthScheme
from schemes.sitaiba_scheme import SitaibaScheme


def setup_multi_scheme_routes(app):
    """Setup all multi-scheme API routes for the Flask app."""
    
    # Register available schemes
    scheme_manager.register_scheme(StealthScheme)
    scheme_manager.register_scheme(SitaibaScheme)
    
    # Auto-activate SITAIBA scheme as default (can be changed to stealth if preferred)
    scheme_manager.activate_scheme("sitaiba")
    
    @app.route("/api/schemes", methods=["GET"])
    def get_available_schemes():
        """Get list of available cryptographic schemes"""
        try:
            schemes = scheme_manager.get_available_schemes()
            return jsonify({
                "schemes": [
                    {
                        "name": scheme.name,
                        "version": scheme.version,
                        "description": scheme.description,
                        "capabilities": scheme.capabilities,
                        "param_files": scheme.param_files,
                        "author": scheme.author
                    }
                    for scheme in schemes
                ],
                "active_scheme": scheme_manager.get_active_scheme_name()
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/schemes/activate", methods=["POST"])
    def activate_scheme():
        """Activate a specific cryptographic scheme"""
        try:
            data = request.get_json()
            if not data or 'scheme_name' not in data:
                return jsonify({"error": "Please specify scheme_name"}), 400
            
            scheme_name = data['scheme_name']
            success = scheme_manager.activate_scheme(scheme_name)
            
            return jsonify({
                "status": "scheme activated",
                "active_scheme": scheme_name,
                "success": success
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/param_files", methods=["GET"])
    @app.route("/api/param_files", methods=["GET"])
    def get_param_files():
        """Get list of available parameter files for active scheme"""
        try:
            if not scheme_manager.is_scheme_active():
                return jsonify({"error": "No active scheme"}), 400
            
            active_scheme = scheme_manager.get_active_scheme()
            scheme_info = active_scheme.get_info()
            
            # Get parameter files from the param directory
            import os
            import glob
            param_dir = "../param/pbc"
            
            param_files = []
            if os.path.exists(param_dir):
                for file_path in glob.glob(os.path.join(param_dir, "*.param")):
                    file_name = os.path.basename(file_path)
                    # Only include files supported by active scheme
                    if file_name in scheme_info.param_files:
                        file_size = os.path.getsize(file_path)
                        param_files.append({
                            "name": file_name,
                            "path": file_path,
                            "size": file_size
                        })
            
            param_files.sort(key=lambda x: x["name"])
            
            return jsonify({
                "param_files": param_files,
                "scheme_name": scheme_info.name,
                "current": active_scheme.current_param_file
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/setup", methods=["POST"])
    @app.route("/api/setup", methods=["POST"])
    def setup():
        """Initialize the active scheme with selected parameter file"""
        try:
            if not scheme_manager.is_scheme_active():
                return jsonify({"error": "No active scheme. Please activate a scheme first."}), 400
            
            data = request.get_json()
            if not data or 'param_file' not in data:
                return jsonify({"error": "Please specify param_file"}), 400
            
            param_file = data['param_file']
            result = scheme_manager.setup_system(param_file)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/status", methods=["GET"])
    @app.route("/api/status", methods=["GET"])
    def status():
        """Get system status including active scheme information"""
        try:
            return jsonify(scheme_manager.get_status())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/reset", methods=["POST"])
    @app.route("/api/reset", methods=["POST"])
    def reset_system():
        """Reset the active scheme state"""
        try:
            if not scheme_manager.is_scheme_active():
                return jsonify({"error": "No active scheme"}), 400
            
            result = scheme_manager.reset_system()
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Dynamic operation routes - check capabilities before executing
    @app.route("/keygen", methods=["GET"])
    @app.route("/api/keygen", methods=["GET"])
    def keygen():
        """Generate a new key pair using active scheme and return in standardized format"""
        try:
            if not scheme_manager.supports_capability('keygen'):
                return jsonify({"error": "Key generation not supported by active scheme"}), 400
            
            # Generate the key
            result = scheme_manager.generate_keypair()
            
            # Get the latest key in standardized format for frontend compatibility
            normalized_keys = scheme_manager.get_keys_normalized()
            if normalized_keys:
                latest_key = normalized_keys[-1]  # Get the most recently generated key
                # Add the original status and any additional fields from result
                latest_key.update({
                    "status": result.get("status", "keypair generated"),
                    "key_size": result.get("key_size", latest_key.get("key_size"))
                })
                return jsonify(latest_key)
            
            # Fallback to original result if normalization fails
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/keylist", methods=["GET"])
    @app.route("/api/keylist", methods=["GET"])
    def keylist():
        """Get list of all generated keys from active scheme in standardized format"""
        try:
            return jsonify(scheme_manager.get_keys_normalized())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/addrgen", methods=["POST"])
    @app.route("/api/addrgen", methods=["POST"])
    def addrgen():
        """Generate address using active scheme"""
        try:
            if not scheme_manager.supports_capability('addrgen'):
                return jsonify({"error": "Address generation not supported by active scheme"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request data required"}), 400
            
            # Map frontend parameter names to backend expected names
            if 'key_index' in data:
                key_index = data.pop('key_index')
                # Get the keys to find the actual key_id from the index
                keys = scheme_manager.get_keys_normalized()
                if key_index < 0 or key_index >= len(keys):
                    return jsonify({"error": f"Invalid key index: {key_index}"}), 400
                
                selected_key = keys[key_index]
                # Extract the actual key_id from the key
                data['key_id'] = selected_key.get('index', key_index)
            
            result = scheme_manager.generate_address(**data)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/addresslist", methods=["GET"])
    @app.route("/api/addresslist", methods=["GET"])
    def addresslist():
        """Get list of all generated addresses from active scheme"""
        try:
            return jsonify(scheme_manager.get_addresses())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/verify_addr", methods=["POST"])
    @app.route("/api/verify_addr", methods=["POST"])
    def verify_addr():
        """Verify address using active scheme"""
        try:
            if not scheme_manager.supports_capability('verify_addr'):
                return jsonify({"error": "Address verification not supported by active scheme"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request data required"}), 400
            
            # Handle parameter mapping for different schemes
            active_scheme_name = scheme_manager.get_active_scheme_name()
            
            if active_scheme_name == "stealth":
                # Map frontend parameter names to stealth expected names
                if 'address_index' in data:
                    addr_index = data.pop('address_index')
                    addresses = scheme_manager.get_addresses()
                    if addr_index < 0 or addr_index >= len(addresses):
                        return jsonify({"error": f"Invalid address index: {addr_index}"}), 400
                    data['addr_id'] = addr_index
                    
                if 'key_index' in data:
                    key_index = data.pop('key_index')
                    keys = scheme_manager.get_keys_normalized()
                    if key_index < 0 or key_index >= len(keys):
                        return jsonify({"error": f"Invalid key index: {key_index}"}), 400
                    data['key_id'] = keys[key_index].get('index', key_index)
            
            # sitaiba and other schemes: no parameter mapping needed
            
            result = scheme_manager.verify_address(**data)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/dskgen", methods=["POST"])
    @app.route("/api/dskgen", methods=["POST"])
    def dskgen():
        """Generate DSK using active scheme"""
        try:
            if not scheme_manager.supports_capability('dskgen'):
                return jsonify({"error": "DSK generation not supported by active scheme"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request data required"}), 400
            
            # Handle parameter mapping for different schemes
            active_scheme_name = scheme_manager.get_active_scheme_name()
            
            if active_scheme_name == "stealth":
                # Map frontend parameter names to stealth expected names
                if 'address_index' in data:
                    addr_index = data.pop('address_index')
                    addresses = scheme_manager.get_addresses()
                    if addr_index < 0 or addr_index >= len(addresses):
                        return jsonify({"error": f"Invalid address index: {addr_index}"}), 400
                    data['addr_id'] = addr_index
                    
                if 'key_index' in data:
                    key_index = data.pop('key_index')
                    keys = scheme_manager.get_keys_normalized()
                    if key_index < 0 or key_index >= len(keys):
                        return jsonify({"error": f"Invalid key index: {key_index}"}), 400
                    data['key_id'] = keys[key_index].get('index', key_index)
            
            # sitaiba and other schemes: no parameter mapping needed
            
            result = scheme_manager.generate_dsk(**data)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/dsklist", methods=["GET"])
    @app.route("/api/dsklist", methods=["GET"])
    def dsklist():
        """Get list of all generated DSKs from active scheme"""
        try:
            return jsonify(scheme_manager.get_dsks())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/sign", methods=["POST"])
    @app.route("/api/sign", methods=["POST"])
    def sign_message():
        """Sign message using active scheme"""
        try:
            if not scheme_manager.supports_capability('sign'):
                return jsonify({"error": "Message signing not supported by active scheme"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request data required"}), 400
            
            # Handle parameter mapping for different schemes
            active_scheme_name = scheme_manager.get_active_scheme_name()
            
            if active_scheme_name == "stealth":
                # Map frontend parameter names to stealth expected names
                if 'dsk_index' in data:
                    dsk_index = data.pop('dsk_index')
                    dsks = scheme_manager.get_dsks()
                    if dsk_index < 0 or dsk_index >= len(dsks):
                        return jsonify({"error": f"Invalid DSK index: {dsk_index}"}), 400
                    data['dsk_id'] = dsk_index
            
            # sitaiba and other schemes: no parameter mapping needed
            
            result = scheme_manager.sign_message(**data)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/verify_signature", methods=["POST"])
    @app.route("/api/verify_signature", methods=["POST"])
    def verify_signature():
        """Verify signature using active scheme"""
        try:
            if not scheme_manager.supports_capability('verify'):
                return jsonify({"error": "Signature verification not supported by active scheme"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request data required"}), 400
            
            # Handle different parameter formats for different schemes
            active_scheme_name = scheme_manager.get_active_scheme_name()
            
            if active_scheme_name == "stealth":
                # Stealth accepts individual signature components from frontend
                # Frontend sends: message, q_sigma_hex, h_hex, address_index
                # We need to pass these directly to stealth scheme
                if 'address_index' in data:
                    addr_index = data.pop('address_index')
                    addresses = scheme_manager.get_addresses()
                    if addr_index < 0 or addr_index >= len(addresses):
                        return jsonify({"error": f"Invalid address index: {addr_index}"}), 400
                    data['addr_id'] = addr_index
            
            # sitaiba and other schemes: expect sig_id parameter
            
            result = scheme_manager.verify_signature(**data)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/trace", methods=["POST"])
    @app.route("/api/trace", methods=["POST"])
    def trace_identity():
        """Trace identity using active scheme"""
        try:
            if not scheme_manager.supports_capability('trace'):
                return jsonify({"error": "Identity tracing not supported by active scheme"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request data required"}), 400
            
            # Handle parameter mapping for different schemes
            active_scheme_name = scheme_manager.get_active_scheme_name()
            
            if active_scheme_name == "stealth":
                # Map frontend parameter names to stealth expected names
                if 'address_index' in data:
                    addr_index = data.pop('address_index')
                    addresses = scheme_manager.get_addresses()
                    if addr_index < 0 or addr_index >= len(addresses):
                        return jsonify({"error": f"Invalid address index: {addr_index}"}), 400
                    data['addr_id'] = addr_index
            
            # sitaiba and other schemes: no parameter mapping needed
            
            result = scheme_manager.trace_identity(**data)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/performance_test", methods=["POST"])
    @app.route("/api/performance_test", methods=["POST"])
    def performance_test():
        """Run performance test using active scheme"""
        try:
            if not scheme_manager.supports_capability('performance'):
                return jsonify({"error": "Performance test not supported by active scheme"}), 400
            
            data = request.get_json()
            kwargs = data if data else {}
            result = scheme_manager.performance_test(**kwargs)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/tx_messages", methods=["GET"])
    @app.route("/api/tx_messages", methods=["GET"])
    def get_tx_messages():
        """Get list of all transaction messages from active scheme"""
        try:
            return jsonify(scheme_manager.get_signatures())
        except Exception as e:
            return jsonify({"error": str(e)}), 500