"""
Multi-Scheme Stealth Demo Server
Updated Flask backend supporting multiple cryptographic schemes
"""

from flask import Flask, request, jsonify, send_from_directory
from ctypes import *
import os
import glob
import traceback
from scheme_manager import SchemeManager

# Initialize scheme manager
scheme_manager = SchemeManager()

# Global state
key_list = []
address_list = []
dsk_list = []
tx_message_list = [] 
trace_key = None
current_param_file = None

app = Flask(__name__, static_folder="../frontend")

# Helper functions
def get_lib():
    """Get current library from scheme manager"""
    try:
        return scheme_manager.get_lib()
    except Exception as e:
        raise Exception("No scheme loaded. Please select a scheme first.")

def get_function_prefix():
    """Get current scheme function prefix"""
    return scheme_manager.get_function_prefix()

def ensure_scheme_loaded():
    """Ensure a scheme is loaded"""
    if not scheme_manager.current_scheme:
        raise Exception("No cryptographic scheme selected. Please select a scheme first.")

def ensure_initialized():
    """Ensure the current scheme is initialized"""
    ensure_scheme_loaded()
    if not scheme_manager.is_initialized():
        raise Exception("Scheme not initialized. Please run setup first.")

def get_element_size():
    """Get element sizes for buffer allocation"""
    if not scheme_manager.is_initialized():
        return 512
    
    lib = get_lib()
    prefix = get_function_prefix()
    
    try:
        g1_size_func = getattr(lib, f"{prefix}element_size_G1")
        zr_size_func = getattr(lib, f"{prefix}element_size_Zr")
        g1_size = g1_size_func()
        zr_size = zr_size_func()
        return max(g1_size, zr_size, 512)
    except AttributeError:
        # ECC-based schemes might not have these functions
        return 512

def bytes_to_hex_safe_fixed(buf, element_type='G1'):
    """Convert bytes buffer to hex string"""
    if not scheme_manager.is_initialized():
        return ""
    
    lib = get_lib()
    prefix = get_function_prefix()
    
    try:
        if element_type == 'G1':
            size_func = getattr(lib, f"{prefix}element_size_G1")
            expected_size = size_func()
        elif element_type == 'Zr':
            size_func = getattr(lib, f"{prefix}element_size_Zr")
            expected_size = size_func()
        else:
            expected_size = len(buf.raw)
    except AttributeError:
        # For ECC-based schemes, use buffer size
        expected_size = len(buf.raw)
    
    if expected_size > len(buf.raw):
        expected_size = len(buf.raw)
    
    data = buf.raw[:expected_size]
    
    if all(b == 0 for b in data):
        return ""
    
    return data.hex()

def hex_to_bytes_safe(hex_str):
    """Safely convert hex string to bytes"""
    try:
        if len(hex_str) % 2 != 0:
            raise ValueError("Hex string length must be even")
        return bytes.fromhex(hex_str)
    except ValueError as e:
        raise ValueError(f"Invalid hex string: {str(e)}")

@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler"""
    error_info = {
        "error": str(e),
        "type": type(e).__name__
    }
    
    if app.debug:
        error_info["traceback"] = traceback.format_exc()
    
    return jsonify(error_info), 500

@app.route("/")
def index():
    return send_from_directory("../frontend-react/dist", "index.html")

@app.route("/schemes", methods=["GET"])
def get_schemes():
    """Get list of available cryptographic schemes"""
    try:
        schemes = scheme_manager.get_available_schemes()
        current = scheme_manager.get_current_scheme()
        
        return jsonify({
            "schemes": schemes,
            "current": current
        })
    except Exception as e:
        raise e

@app.route("/schemes/<scheme_id>", methods=["POST"])
def switch_scheme(scheme_id):
    """Switch to a different cryptographic scheme"""
    try:
        # Clear existing data when switching schemes
        global key_list, address_list, dsk_list, trace_key, current_param_file
        key_list.clear()
        address_list.clear()
        dsk_list.clear()
        tx_message_list.clear()
        trace_key = None
        current_param_file = None
        
        result = scheme_manager.switch_scheme(scheme_id)
        
        return jsonify({
            "status": "success",
            "message": f"Switched to {result['name']}",
            "scheme": result
        })
    except Exception as e:
        raise e

@app.route("/param_files", methods=["GET"])
def get_param_files():
    """Get list of available parameter files"""
    try:
        ensure_scheme_loaded()
        current_scheme = scheme_manager.get_current_scheme()
        
        if current_scheme['param_type'] == 'pbc':
            param_dir = "../param"
        else:
            param_dir = "../param/ecc_params"  # For ECC-based schemes
        
        if not os.path.exists(param_dir):
            return jsonify({"error": f"Parameter directory not found: {param_dir}"}), 404
        
        param_files = []
        file_pattern = "*.param" if current_scheme['param_type'] == 'pbc' else "*"
        
        for file_path in glob.glob(os.path.join(param_dir, file_pattern)):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            param_files.append({
                "name": file_name,
                "path": file_path,
                "size": file_size
            })
        
        param_files.sort(key=lambda x: x["name"])
        
        return jsonify({
            "param_files": param_files,
            "current": current_param_file,
            "param_type": current_scheme['param_type']
        })
    except Exception as e:
        raise e

@app.route("/setup", methods=["POST"])
def setup():
    """Initialize the current scheme with selected parameter file"""
    global trace_key, current_param_file
    
    try:
        ensure_scheme_loaded()
        
        data = request.get_json()
        if not data or 'param_file' not in data:
            return jsonify({"error": "Please specify param_file"}), 400
        
        param_file = data['param_file']
        current_scheme = scheme_manager.get_current_scheme()
        
        if current_scheme['param_type'] == 'pbc':
            full_path = os.path.join("../param", param_file)
        else:
            full_path = os.path.join("../param/ecc_params", param_file)
        
        if not os.path.exists(full_path):
            return jsonify({"error": f"Parameter file not found: {param_file}"}), 404
        
        lib = get_lib()
        prefix = get_function_prefix()
        
        print(f"🔧 Initializing {current_scheme['name']} with {full_path}")
        
        init_func = getattr(lib, f"{prefix}init")
        result = init_func(full_path.encode())
        
        if result != 0:
            raise Exception(f"Scheme initialization failed with code: {result}")
        
        # Check if scheme has is_initialized function
        try:
            is_init_func = getattr(lib, f"{prefix}is_initialized")
            if not is_init_func():
                raise Exception("Scheme initialization verification failed")
        except AttributeError:
            # Some schemes might not have this function
            pass
        
        scheme_manager.mark_initialized()
        current_param_file = param_file
        
        # Generate trace key if supported
        if scheme_manager.is_function_available('tracekeygen'):
            buf_size = get_element_size()
            TK_buf = create_string_buffer(buf_size)
            k_buf = create_string_buffer(buf_size)
            
            for i in range(buf_size):
                TK_buf[i] = 0
                k_buf[i] = 0
            
            tracekeygen_func = getattr(lib, f"{prefix}tracekeygen_simple")
            tracekeygen_func(TK_buf, k_buf, buf_size)
            
            tk_hex = bytes_to_hex_safe_fixed(TK_buf, 'G1')
            k_hex = bytes_to_hex_safe_fixed(k_buf, 'Zr')
            
            if not tk_hex or not k_hex:
                raise Exception("Failed to generate trace key")
            
            trace_key = {
                "TK_hex": tk_hex,
                "k_hex": k_hex,
                "param_file": param_file,
                "status": "initialized"
            }
        else:
            trace_key = None
        
        # Clear existing data
        key_list.clear()
        address_list.clear()
        dsk_list.clear()
        tx_message_list.clear()
        
        response = {
            "status": "setup complete",
            "message": f"Scheme {current_scheme['name']} initialized with {param_file}",
            "scheme": current_scheme['id'],
            "param_file": param_file,
            "param_type": current_scheme['param_type'],
            "available_functions": current_scheme['functions']
        }
        
        # Add element sizes for PBC schemes
        if current_scheme['param_type'] == 'pbc':
            try:
                g1_size_func = getattr(lib, f"{prefix}element_size_G1")
                zr_size_func = getattr(lib, f"{prefix}element_size_Zr")
                response["g1_size"] = g1_size_func()
                response["zr_size"] = zr_size_func()
            except AttributeError:
                pass
        
        if trace_key:
            response.update(trace_key)
        
        return jsonify(response)
        
    except Exception as e:
        scheme_manager.initialized = False
        current_param_file = None
        raise e

@app.route("/keygen", methods=["GET"])
def keygen():
    """Generate a new key pair"""
    try:
        ensure_initialized()
        
        if not scheme_manager.is_function_available('keygen'):
            return jsonify({"error": "Key generation not supported by current scheme"}), 400
        
        lib = get_lib()
        prefix = get_function_prefix()
        buf_size = get_element_size()
        
        A_buf = create_string_buffer(buf_size)
        B_buf = create_string_buffer(buf_size)
        a_buf = create_string_buffer(buf_size)
        b_buf = create_string_buffer(buf_size)
        
        for buf in [A_buf, B_buf, a_buf, b_buf]:
            for i in range(buf_size):
                buf[i] = 0
        
        keygen_func = getattr(lib, f"{prefix}keygen_simple")
        keygen_func(A_buf, B_buf, a_buf, b_buf, buf_size)
        
        A_hex = bytes_to_hex_safe_fixed(A_buf, 'G1')
        B_hex = bytes_to_hex_safe_fixed(B_buf, 'G1')
        a_hex = bytes_to_hex_safe_fixed(a_buf, 'Zr')
        b_hex = bytes_to_hex_safe_fixed(b_buf, 'Zr')
        
        if not A_hex or not B_hex or not a_hex or not b_hex:
            raise Exception("Failed to generate key pair")
        
        item = {
            "index": len(key_list),
            "id": f"key_{len(key_list)}",
            "A_hex": A_hex,
            "B_hex": B_hex,
            "a_hex": a_hex,
            "b_hex": b_hex,
            "scheme": scheme_manager.current_scheme,
            "param_file": current_param_file,
            "status": "generated"
        }
        
        key_list.append(item)
        return jsonify(item)
        
    except Exception as e:
        raise e

@app.route("/keylist", methods=["GET"])
def keylist():
    """Get list of all generated keys"""
    return jsonify(key_list)

@app.route("/status", methods=["GET"])
def status():
    """Get system status"""
    current_scheme = scheme_manager.get_current_scheme()
    
    status_info = {
        "scheme_loaded": current_scheme is not None,
        "initialized": scheme_manager.is_initialized(),
        "param_file": current_param_file,
        "trace_key_set": trace_key is not None,
        "keys_count": len(key_list),
        "addresses_count": len(address_list),
        "dsks_count": len(dsk_list),
        "tx_messages_count": len(tx_message_list),
        "available_schemes_count": len([s for s in scheme_manager.get_available_schemes() if s['available']])
    }
    
    if current_scheme:
        status_info.update({
            "current_scheme": current_scheme,
            "available_functions": current_scheme['functions']
        })
        
        # Add element sizes for PBC schemes
        if current_scheme['param_type'] == 'pbc' and scheme_manager.is_initialized():
            try:
                lib = get_lib()
                prefix = get_function_prefix()
                g1_size_func = getattr(lib, f"{prefix}element_size_G1")
                zr_size_func = getattr(lib, f"{prefix}element_size_Zr")
                status_info.update({
                    "g1_element_size": g1_size_func(),
                    "zr_element_size": zr_size_func()
                })
            except:
                pass
    
    return jsonify(status_info)

@app.route("/reset", methods=["POST"])
def reset_system():
    """Reset the system state"""
    global key_list, address_list, dsk_list, trace_key, current_param_file
    
    try:
        if scheme_manager.is_initialized():
            try:
                lib = get_lib()
                prefix = get_function_prefix()
                reset_func = getattr(lib, f"{prefix}reset_performance", None)
                if reset_func:
                    reset_func()
            except:
                pass  # Ignore reset errors
        
        key_list.clear()
        address_list.clear()
        dsk_list.clear()
        tx_message_list.clear()
        trace_key = None
        current_param_file = None
        scheme_manager.initialized = False
        
        print("🧹 All backend data cleared")
        
        return jsonify({
            "status": "reset complete",
            "message": "All system state has been reset",
            "keys_count": len(key_list),
            "addresses_count": len(address_list)
        })
    except Exception as e:
        raise e

# Additional endpoints for address generation, verification, signing, etc.
# These will be similar to the original app.py but with dynamic function calls
# based on the current scheme

if __name__ == "__main__":
    print("🚀 Starting Multi-Scheme Stealth Demo Server")
    print("🎯 Features: Multiple cryptographic schemes support")
    print("💡 Schemes: my_stealth, cryptonote2, zhao, hdwsa, sitaiba")
    print("🌐 Server will run on http://localhost:5000")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        try:
            if scheme_manager.is_initialized():
                lib = get_lib()
                prefix = get_function_prefix()
                cleanup_func = getattr(lib, f"{prefix}cleanup", None)
                if cleanup_func:
                    cleanup_func()
                print("🧹 Library cleanup completed")
        except:
            pass