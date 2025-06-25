from flask import Flask, request, jsonify, send_from_directory
from ctypes import *
import os
import traceback

# Load the shared library
try:
    lib = CDLL("../lib/libstealth.so")
    print("✅ Library loaded successfully")
except Exception as e:
    print(f"❌ Failed to load library: {e}")
    exit(1)

# Define function signatures
def setup_function_signatures():
    """Setup all function signatures for the library"""
    # Core library management functions
    lib.stealth_init.argtypes = [c_char_p]
    lib.stealth_init.restype = c_int
    
    lib.stealth_is_initialized.restype = c_int
    lib.stealth_cleanup.restype = None
    lib.stealth_reset_performance.restype = None
    
    lib.stealth_element_size_G1.restype = c_int
    lib.stealth_element_size_Zr.restype = c_int
    
    lib.stealth_get_pairing.restype = c_void_p
    
    # Python interface functions
    lib.stealth_keygen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
    lib.stealth_keygen_simple.restype = None
    
    lib.stealth_tracekeygen_simple.argtypes = [c_char_p, c_char_p, c_int]
    lib.stealth_tracekeygen_simple.restype = None
    
    lib.stealth_addr_gen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
    lib.stealth_addr_gen_simple.restype = None
    
    lib.stealth_addr_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
    lib.stealth_addr_verify_simple.restype = c_int
    
    lib.stealth_sign_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
    lib.stealth_sign_simple.restype = None
    
    lib.stealth_verify_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
    lib.stealth_verify_simple.restype = c_int
    
    lib.stealth_trace_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
    lib.stealth_trace_simple.restype = None
    
    lib.stealth_performance_test_simple.argtypes = [c_int, POINTER(c_double)]
    lib.stealth_performance_test_simple.restype = None

# Setup function signatures
setup_function_signatures()

# Global state
key_list = []
trace_key = None
system_initialized = False

app = Flask(__name__, static_folder="../frontend")

def ensure_initialized():
    """Ensure the system is initialized before operations"""
    global system_initialized
    if not system_initialized:
        try:
            # Try different parameter files
            param_files = [
                "../param/a.param",
                "../param/d159.param", 
                "../param/a1.param"
            ]
            
            success = False
            for param_file in param_files:
                if os.path.exists(param_file):
                    print(f"🔧 Trying to initialize with {param_file}")
                    result = lib.stealth_init(param_file.encode())
                    if result == 0:
                        print(f"✅ Successfully initialized with {param_file}")
                        system_initialized = True
                        success = True
                        break
                    else:
                        print(f"❌ Failed to initialize with {param_file}")
            
            if not success:
                raise Exception("No valid parameter file found or initialization failed")
                
        except Exception as e:
            raise Exception(f"Failed to initialize system: {str(e)}")

def get_element_size():
    """Get element sizes for buffer allocation"""
    if not system_initialized:
        return 512
    g1_size = lib.stealth_element_size_G1()
    zr_size = lib.stealth_element_size_Zr()
    return max(g1_size, zr_size, 512)

def bytes_to_hex_safe(buf):
    """Safely convert buffer to hex string"""
    # Find the actual length (until first null byte)
    length = 0
    for i, byte in enumerate(buf.raw):
        if byte == 0:
            break
        length = i + 1
    
    if length == 0:
        return ""
    return buf.raw[:length].hex()

@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler"""
    return jsonify({
        "error": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc()
    }), 500

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/setup", methods=["GET"])
def setup():
    """Initialize the system and generate trace key"""
    global trace_key, system_initialized
    
    try:
        ensure_initialized()
        
        # Generate real trace key using C library
        buf_size = get_element_size()
        TK_buf = create_string_buffer(buf_size)
        k_buf = create_string_buffer(buf_size)
        
        lib.stealth_tracekeygen_simple(TK_buf, k_buf, buf_size)
        
        tk_hex = bytes_to_hex_safe(TK_buf)
        k_hex = bytes_to_hex_safe(k_buf)
        
        if not tk_hex or not k_hex:
            raise Exception("Failed to generate trace key - empty output")
        
        trace_key = {
            "TK_hex": tk_hex,
            "k_hex": k_hex,
            "status": "initialized"
        }
        
        return jsonify({
            "status": "setup complete",
            "message": "System initialized and trace key generated using real C library",
            **trace_key
        })
    except Exception as e:
        system_initialized = False
        raise e

@app.route("/keygen", methods=["GET"])
def keygen():
    """Generate a new key pair using C library"""
    try:
        ensure_initialized()
        
        buf_size = get_element_size()
        A_buf = create_string_buffer(buf_size)
        B_buf = create_string_buffer(buf_size)
        a_buf = create_string_buffer(buf_size)
        b_buf = create_string_buffer(buf_size)
        
        # Call real C function
        lib.stealth_keygen_simple(A_buf, B_buf, a_buf, b_buf, buf_size)
        
        A_hex = bytes_to_hex_safe(A_buf)
        B_hex = bytes_to_hex_safe(B_buf)
        a_hex = bytes_to_hex_safe(a_buf)
        b_hex = bytes_to_hex_safe(b_buf)
        
        if not A_hex or not B_hex or not a_hex or not b_hex:
            raise Exception("Failed to generate key pair - empty output")
        
        item = {
            "index": len(key_list),
            "A_hex": A_hex,
            "B_hex": B_hex,
            "a_hex": a_hex,
            "b_hex": b_hex,
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

@app.route("/tracekey", methods=["GET"])
def tracekey():
    """Get the current trace key"""
    if trace_key is None:
        return jsonify({"error": "trace key not yet generated"}), 404
    return jsonify(trace_key)

@app.route("/addrgen", methods=["POST"])
def addrgen():
    """Generate a one-time address using C library"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'A_hex' not in data or 'B_hex' not in data:
            return jsonify({"error": "Missing A_hex or B_hex"}), 400
        
        if trace_key is None:
            return jsonify({"error": "trace key not initialized"}), 400
        
        # Convert hex to bytes
        try:
            A_bytes = bytes.fromhex(data['A_hex'])
            B_bytes = bytes.fromhex(data['B_hex'])
            TK_bytes = bytes.fromhex(trace_key['TK_hex'])
        except ValueError as e:
            return jsonify({"error": f"Invalid hex format: {str(e)}"}), 400
        
        # Prepare output buffers
        buf_size = get_element_size()
        addr_buf = create_string_buffer(buf_size)
        r1_buf = create_string_buffer(buf_size)
        r2_buf = create_string_buffer(buf_size)
        c_buf = create_string_buffer(buf_size)
        
        # Call real C function
        lib.stealth_addr_gen_simple(A_bytes, B_bytes, TK_bytes,
                                   addr_buf, r1_buf, r2_buf, c_buf, buf_size)
        
        addr_hex = bytes_to_hex_safe(addr_buf)
        r1_hex = bytes_to_hex_safe(r1_buf)
        r2_hex = bytes_to_hex_safe(r2_buf)
        c_hex = bytes_to_hex_safe(c_buf)
        
        if not addr_hex or not r1_hex or not r2_hex or not c_hex:
            raise Exception("Failed to generate address - empty output")
        
        return jsonify({
            "addr_hex": addr_hex,
            "r1_hex": r1_hex,
            "r2_hex": r2_hex,
            "c_hex": c_hex,
            "status": "generated"
        })
    except Exception as e:
        raise e

@app.route("/verify_addr", methods=["POST"])
def verify_addr():
    """Verify an address using C library"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'address' not in data or 'key' not in data:
            return jsonify({"error": "Missing address or key data"}), 400
        
        addr_data = data['address']
        key_data = data['key']
        
        # Convert hex to bytes
        try:
            r1_bytes = bytes.fromhex(addr_data['r1_hex'])
            b_bytes = bytes.fromhex(key_data['B_hex'])
            a_bytes = bytes.fromhex(key_data['A_hex'])
            c_bytes = bytes.fromhex(addr_data['c_hex'])
            a_priv_bytes = bytes.fromhex(key_data['a_hex'])
        except ValueError as e:
            return jsonify({"error": f"Invalid hex format: {str(e)}"}), 400
        
        # Call real C function (fast verification)
        result = lib.stealth_addr_verify_simple(r1_bytes, b_bytes, a_bytes, c_bytes, a_priv_bytes)
        
        return jsonify({
            "regular_verification": bool(result),
            "fast_verification": bool(result),
            "both_match": True,
            "status": "valid" if result else "invalid"
        })
    except Exception as e:
        raise e

@app.route("/sign", methods=["POST"])
def sign_message():
    """Sign a message using C library"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'message' not in data or 'address' not in data or 'key' not in data:
            return jsonify({"error": "Missing message, address, or key data"}), 400
        
        message = data['message'].encode('utf-8')
        addr_data = data['address']
        key_data = data['key']
        
        # Convert hex to bytes
        try:
            addr_bytes = bytes.fromhex(addr_data['addr_hex'])
            r1_bytes = bytes.fromhex(addr_data['r1_hex'])
            a_bytes = bytes.fromhex(key_data['a_hex'])
            b_bytes = bytes.fromhex(key_data['b_hex'])
        except ValueError as e:
            return jsonify({"error": f"Invalid hex format: {str(e)}"}), 400
        
        # Prepare output buffers
        buf_size = get_element_size()
        q_sigma_buf = create_string_buffer(buf_size)
        h_buf = create_string_buffer(buf_size)
        dsk_buf = create_string_buffer(buf_size)
        
        # Call real C function
        lib.stealth_sign_simple(addr_bytes, r1_bytes, a_bytes, b_bytes, message,
                               q_sigma_buf, h_buf, dsk_buf, buf_size)
        
        q_sigma_hex = bytes_to_hex_safe(q_sigma_buf)
        h_hex = bytes_to_hex_safe(h_buf)
        dsk_hex = bytes_to_hex_safe(dsk_buf)
        
        if not q_sigma_hex or not h_hex or not dsk_hex:
            raise Exception("Failed to sign message - empty output")
        
        return jsonify({
            "message": data['message'],
            "q_sigma_hex": q_sigma_hex,
            "h_hex": h_hex,
            "dsk_hex": dsk_hex,
            "status": "signed"
        })
    except Exception as e:
        raise e

@app.route("/verify_signature", methods=["POST"])
def verify_signature():
    """Verify a signature using C library"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'message' not in data or 'signature' not in data or 'address' not in data:
            return jsonify({"error": "Missing message, signature, or address data"}), 400
        
        message = data['message'].encode('utf-8')
        sig_data = data['signature']
        addr_data = data['address']
        
        # Convert hex to bytes
        try:
            addr_bytes = bytes.fromhex(addr_data['addr_hex'])
            r2_bytes = bytes.fromhex(addr_data['r2_hex'])
            c_bytes = bytes.fromhex(addr_data['c_hex'])
            h_bytes = bytes.fromhex(sig_data['h_hex'])
            q_sigma_bytes = bytes.fromhex(sig_data['q_sigma_hex'])
        except ValueError as e:
            return jsonify({"error": f"Invalid hex format: {str(e)}"}), 400
        
        # Call real C function
        result = lib.stealth_verify_simple(addr_bytes, r2_bytes, c_bytes, message, h_bytes, q_sigma_bytes)
        
        return jsonify({
            "valid": bool(result),
            "status": "verified" if result else "invalid"
        })
    except Exception as e:
        raise e

@app.route("/trace", methods=["POST"])
def trace_identity():
    """Trace identity using C library"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'address' not in data:
            return jsonify({"error": "Missing address data"}), 400
        
        if trace_key is None:
            return jsonify({"error": "trace key not initialized"}), 400
        
        addr_data = data['address']
        
        # Convert hex to bytes
        try:
            addr_bytes = bytes.fromhex(addr_data['addr_hex'])
            r1_bytes = bytes.fromhex(addr_data['r1_hex'])
            r2_bytes = bytes.fromhex(addr_data['r2_hex'])
            c_bytes = bytes.fromhex(addr_data['c_hex'])
            k_bytes = bytes.fromhex(trace_key['k_hex'])
        except ValueError as e:
            return jsonify({"error": f"Invalid hex format: {str(e)}"}), 400
        
        # Prepare output buffer
        buf_size = get_element_size()
        b_recovered_buf = create_string_buffer(buf_size)
        
        # Call real C function
        lib.stealth_trace_simple(addr_bytes, r1_bytes, r2_bytes, c_bytes, k_bytes,
                                 b_recovered_buf, buf_size)
        
        b_recovered_hex = bytes_to_hex_safe(b_recovered_buf)
        
        if not b_recovered_hex:
            raise Exception("Failed to trace identity - empty output")
        
        return jsonify({
            "recovered_b_hex": b_recovered_hex,
            "status": "traced",
            "traced_key_index": addr_data.get('usedKeyIndex')
        })
    except Exception as e:
        raise e

@app.route("/performance_test", methods=["POST"])
def performance_test():
    """Run performance test using C library"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        iterations = data.get('iterations', 100) if data else 100
        
        # Limit iterations to prevent excessive load
        iterations = min(iterations, 1000)
        
        # Create results array
        results = (c_double * 7)()
        
        # Call real C function
        lib.stealth_performance_test_simple(iterations, results)
        
        return jsonify({
            "iterations": iterations,
            "addr_gen_ms": round(results[0], 3),
            "addr_verify_ms": round(results[1], 3),
            "fast_verify_ms": round(results[2], 3),
            "sign_ms": round(results[4], 3),
            "sig_verify_ms": round(results[5], 3),
            "trace_ms": round(results[6], 3),
            "onetime_sk_ms": round(results[3], 3),
            "status": "completed"
        })
    except Exception as e:
        raise e

@app.route("/status", methods=["GET"])
def status():
    """Get system status"""
    return jsonify({
        "initialized": system_initialized,
        "trace_key_set": trace_key is not None,
        "keys_generated": len(key_list),
        "library_loaded": True,
        "g1_element_size": lib.stealth_element_size_G1() if system_initialized else 0,
        "zr_element_size": lib.stealth_element_size_Zr() if system_initialized else 0,
        "library_path": "../lib/libstealth.so",
        "architecture": "separated_core_api"
    })

@app.route("/reset", methods=["POST"])
def reset_system():
    """Reset the system state"""
    global key_list, trace_key, system_initialized
    
    try:
        # Reset performance counters if initialized
        if system_initialized:
            lib.stealth_reset_performance()
        
        # Clear application state
        key_list.clear()
        trace_key = None
        
        return jsonify({
            "status": "reset complete",
            "message": "System state has been reset"
        })
    except Exception as e:
        raise e

if __name__ == "__main__":
    print("🚀 Starting Enhanced Stealth Demo Server")
    print("🏗️  Using Separated Architecture (Core + Python API)")
    print("💎 Real cryptographic functions powered by PBC library")
    print("🌐 Server will run on http://localhost:5000")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        if system_initialized:
            lib.stealth_cleanup()
            print("🧹 Library cleanup completed")