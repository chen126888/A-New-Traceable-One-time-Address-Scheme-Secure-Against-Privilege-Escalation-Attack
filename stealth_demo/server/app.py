from flask import Flask, request, jsonify, send_from_directory
from ctypes import *
import os
import glob
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
    
    # Existing Python interface functions
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
    
    # New DSK functions (will be added after C compilation)
    try:
        lib.stealth_dsk_gen_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        lib.stealth_dsk_gen_simple.restype = None
        
        lib.stealth_sign_with_dsk_simple.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
        lib.stealth_sign_with_dsk_simple.restype = None
        
        print("✅ New DSK functions loaded")
        global DSK_FUNCTIONS_AVAILABLE
        DSK_FUNCTIONS_AVAILABLE = True
    except AttributeError:
        print("⚠️ DSK functions not available - using fallback implementation")
        DSK_FUNCTIONS_AVAILABLE = False
    
    lib.stealth_performance_test_simple.argtypes = [c_int, POINTER(c_double)]
    lib.stealth_performance_test_simple.restype = None

# Setup function signatures
DSK_FUNCTIONS_AVAILABLE = False
setup_function_signatures()

# Global state
key_list = []
address_list = []
dsk_list = []
trace_key = None
system_initialized = False
current_param_file = None

app = Flask(__name__, static_folder="../frontend")

def ensure_initialized():
    """Ensure the system is initialized before operations"""
    global system_initialized
    if not system_initialized:
        raise Exception("System not initialized. Please run setup first.")

def get_element_size():
    """Get element sizes for buffer allocation"""
    if not system_initialized:
        return 512
    g1_size = lib.stealth_element_size_G1()
    zr_size = lib.stealth_element_size_Zr()
    return max(g1_size, zr_size, 512)

def bytes_to_hex_safe_fixed(buf, element_type='G1'):
    """Fixed version of bytes_to_hex_safe - uses fixed size, doesn't remove zero bytes"""
    if not system_initialized:
        return ""
    
    if element_type == 'G1':
        expected_size = lib.stealth_element_size_G1()
    elif element_type == 'Zr':
        expected_size = lib.stealth_element_size_Zr()
    else:
        raise ValueError(f"Unknown element type: {element_type}")
    
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
    return send_from_directory("../frontend", "index.html")

@app.route("/param_files", methods=["GET"])
def get_param_files():
    """Get list of available parameter files"""
    try:
        param_dir = "../param"
        if not os.path.exists(param_dir):
            return jsonify({"error": "Parameter directory not found"}), 404
        
        param_files = []
        for file_path in glob.glob(os.path.join(param_dir, "*.param")):
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
            "current": current_param_file
        })
    except Exception as e:
        raise e

@app.route("/setup", methods=["POST"])
def setup():
    """Initialize the system with selected parameter file"""
    global trace_key, system_initialized, current_param_file
    
    try:
        data = request.get_json()
        if not data or 'param_file' not in data:
            return jsonify({"error": "Please specify param_file"}), 400
        
        param_file = data['param_file']
        full_path = os.path.join("../param", param_file)
        
        if not os.path.exists(full_path):
            return jsonify({"error": f"Parameter file not found: {param_file}"}), 404
        
        print(f"🔧 Initializing with {full_path}")
        result = lib.stealth_init(full_path.encode())
        
        if result != 0:
            raise Exception(f"Library initialization failed with code: {result}")
        
        if not lib.stealth_is_initialized():
            raise Exception("Library initialization verification failed")
        
        system_initialized = True
        current_param_file = param_file
        
        # Generate trace key
        buf_size = get_element_size()
        TK_buf = create_string_buffer(buf_size)
        k_buf = create_string_buffer(buf_size)
        
        for i in range(buf_size):
            TK_buf[i] = 0
            k_buf[i] = 0
        
        lib.stealth_tracekeygen_simple(TK_buf, k_buf, buf_size)
        
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
        
        # Clear existing data
        key_list.clear()
        address_list.clear()
        dsk_list.clear()
        
        return jsonify({
            "status": "setup complete",
            "message": f"System initialized with {param_file}",
            "param_file": param_file,
            "g1_size": lib.stealth_element_size_G1(),
            "zr_size": lib.stealth_element_size_Zr(),
            "dsk_functions_available": DSK_FUNCTIONS_AVAILABLE,
            **trace_key
        })
        
    except Exception as e:
        system_initialized = False
        current_param_file = None
        raise e

@app.route("/keygen", methods=["GET"])
def keygen():
    """Generate a new key pair"""
    try:
        ensure_initialized()
        
        buf_size = get_element_size()
        
        A_buf = create_string_buffer(buf_size)
        B_buf = create_string_buffer(buf_size)
        a_buf = create_string_buffer(buf_size)
        b_buf = create_string_buffer(buf_size)
        
        for buf in [A_buf, B_buf, a_buf, b_buf]:
            for i in range(buf_size):
                buf[i] = 0
        
        lib.stealth_keygen_simple(A_buf, B_buf, a_buf, b_buf, buf_size)
        
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

@app.route("/addrgen", methods=["POST"])
def addrgen():
    """Generate address with selected key"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'key_index' not in data:
            return jsonify({"error": "Please specify key_index"}), 400
        
        key_index = data['key_index']
        if key_index < 0 or key_index >= len(key_list):
            return jsonify({"error": "Invalid key_index"}), 400
        
        if trace_key is None:
            return jsonify({"error": "Trace key not initialized"}), 400
        
        selected_key = key_list[key_index]
        
        A_hex = selected_key['A_hex']
        B_hex = selected_key['B_hex']
        TK_hex = trace_key['TK_hex']
        
        A_bytes = hex_to_bytes_safe(A_hex)
        B_bytes = hex_to_bytes_safe(B_hex)
        TK_bytes = hex_to_bytes_safe(TK_hex)
        
        buf_size = get_element_size()
        
        addr_buf = create_string_buffer(buf_size)
        r1_buf = create_string_buffer(buf_size)
        r2_buf = create_string_buffer(buf_size)
        c_buf = create_string_buffer(buf_size)
        
        for buf in [addr_buf, r1_buf, r2_buf, c_buf]:
            for i in range(buf_size):
                buf[i] = 0
        
        lib.stealth_addr_gen_simple(A_bytes, B_bytes, TK_bytes,
                                   addr_buf, r1_buf, r2_buf, c_buf, buf_size)
        
        addr_hex = bytes_to_hex_safe_fixed(addr_buf, 'G1')
        r1_hex = bytes_to_hex_safe_fixed(r1_buf, 'G1')
        r2_hex = bytes_to_hex_safe_fixed(r2_buf, 'G1')
        c_hex = bytes_to_hex_safe_fixed(c_buf, 'G1')
        
        if not addr_hex or not r1_hex or not r2_hex or not c_hex:
            raise Exception("Failed to generate address")
        
        address_item = {
            "index": len(address_list),
            "id": f"addr_{len(address_list)}",
            "addr_hex": addr_hex,
            "r1_hex": r1_hex,
            "r2_hex": r2_hex,
            "c_hex": c_hex,
            "key_index": key_index,
            "key_id": selected_key['id'],
            "owner_A": A_hex,
            "owner_B": B_hex,
            "status": "generated"
        }
        
        address_list.append(address_item)
        return jsonify(address_item)
        
    except Exception as e:
        raise e

@app.route("/addresslist", methods=["GET"])
def addresslist():
    """Get list of all generated addresses"""
    return jsonify(address_list)

@app.route("/verify_addr", methods=["POST"])
def verify_addr():
    """Verify address with selected key"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'address_index' not in data or 'key_index' not in data:
            return jsonify({"error": "Please specify address_index and key_index"}), 400
        
        addr_index = data['address_index']
        key_index = data['key_index']
        
        if addr_index < 0 or addr_index >= len(address_list):
            return jsonify({"error": "Invalid address_index"}), 400
        
        if key_index < 0 or key_index >= len(key_list):
            return jsonify({"error": "Invalid key_index"}), 400
        
        address_data = address_list[addr_index]
        key_data = key_list[key_index]
        
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        b_bytes = hex_to_bytes_safe(key_data['B_hex'])
        a_bytes = hex_to_bytes_safe(key_data['A_hex'])
        c_bytes = hex_to_bytes_safe(address_data['c_hex'])
        a_priv_bytes = hex_to_bytes_safe(key_data['a_hex'])
        
        result = lib.stealth_addr_verify_simple(r1_bytes, b_bytes, a_bytes, c_bytes, a_priv_bytes)
        
        return jsonify({
            "valid": bool(result),
            "address_index": addr_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "is_owner": (address_data['key_index'] == key_index),
            "status": "valid" if result else "invalid"
        })
        
    except Exception as e:
        raise e

@app.route("/dskgen", methods=["POST"])
def dskgen():
    """Generate DSK for selected address and key"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'address_index' not in data or 'key_index' not in data:
            return jsonify({"error": "Please specify address_index and key_index"}), 400
        
        addr_index = data['address_index']
        key_index = data['key_index']
        
        if addr_index < 0 or addr_index >= len(address_list):
            return jsonify({"error": "Invalid address_index"}), 400
        
        if key_index < 0 or key_index >= len(key_list):
            return jsonify({"error": "Invalid key_index"}), 400
        
        address_data = address_list[addr_index]
        key_data = key_list[key_index]
        
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        a_bytes = hex_to_bytes_safe(key_data['a_hex'])
        b_bytes = hex_to_bytes_safe(key_data['b_hex'])
        
        buf_size = get_element_size()
        dsk_buf = create_string_buffer(buf_size)
        
        for i in range(buf_size):
            dsk_buf[i] = 0
        
        if DSK_FUNCTIONS_AVAILABLE:
            # Use new dedicated DSK function
            lib.stealth_dsk_gen_simple(addr_bytes, r1_bytes, a_bytes, b_bytes, dsk_buf, buf_size)
        else:
            # Fallback: use the original sign function and extract DSK
            temp_q_buf = create_string_buffer(buf_size)
            temp_h_buf = create_string_buffer(buf_size)
            
            for i in range(buf_size):
                temp_q_buf[i] = 0
                temp_h_buf[i] = 0
            
            lib.stealth_sign_simple(addr_bytes, r1_bytes, a_bytes, b_bytes, b"temp_message",
                                   temp_q_buf, temp_h_buf, dsk_buf, buf_size)
        
        dsk_hex = bytes_to_hex_safe_fixed(dsk_buf, 'G1')
        
        if not dsk_hex:
            raise Exception("Failed to generate DSK")
        
        dsk_item = {
            "index": len(dsk_list),
            "id": f"dsk_{len(dsk_list)}",
            "dsk_hex": dsk_hex,
            "address_index": addr_index,
            "key_index": key_index,
            "address_id": address_data['id'],
            "key_id": key_data['id'],
            "owner_A": key_data['A_hex'],
            "owner_B": key_data['B_hex'],
            "for_address": address_data['addr_hex'],
            "method": "dedicated" if DSK_FUNCTIONS_AVAILABLE else "fallback",
            "status": "generated"
        }
        
        dsk_list.append(dsk_item)
        return jsonify(dsk_item)
        
    except Exception as e:
        raise e

@app.route("/dsklist", methods=["GET"])
def dsklist():
    """Get list of all generated DSKs"""
    return jsonify(dsk_list)

@app.route("/sign", methods=["POST"])
def sign_message():
    """Sign message with selected DSK or key"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Please specify message"}), 400
        
        message = data['message']
        message_bytes = message.encode('utf-8')
        
        # Check if using DSK or key-based signing
        if 'dsk_index' in data:
            # Sign with DSK
            dsk_index = data['dsk_index']
            
            if dsk_index < 0 or dsk_index >= len(dsk_list):
                return jsonify({"error": "Invalid dsk_index"}), 400
            
            dsk_data = dsk_list[dsk_index]
            address_data = address_list[dsk_data['address_index']]
            
            addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
            dsk_bytes = hex_to_bytes_safe(dsk_data['dsk_hex'])
            
            buf_size = get_element_size()
            q_sigma_buf = create_string_buffer(buf_size)
            h_buf = create_string_buffer(buf_size)
            
            for buf in [q_sigma_buf, h_buf]:
                for i in range(buf_size):
                    buf[i] = 0
            
            if DSK_FUNCTIONS_AVAILABLE:
                lib.stealth_sign_with_dsk_simple(addr_bytes, dsk_bytes, message_bytes,
                                                q_sigma_buf, h_buf, buf_size)
            else:
                # Fallback: manual signing logic would go here
                raise Exception("DSK signing not available in fallback mode")
            
            q_sigma_hex = bytes_to_hex_safe_fixed(q_sigma_buf, 'G1')
            h_hex = bytes_to_hex_safe_fixed(h_buf, 'Zr')
            
            if not q_sigma_hex or not h_hex:
                raise Exception("Failed to sign message with DSK")
            
            return jsonify({
                "message": message,
                "q_sigma_hex": q_sigma_hex,
                "h_hex": h_hex,
                "dsk_index": dsk_index,
                "dsk_id": dsk_data['id'],
                "address_index": dsk_data['address_index'],
                "address_id": dsk_data['address_id'],
                "method": "dsk",
                "status": "signed"
            })
            
        elif 'address_index' in data and 'key_index' in data:
            # Sign with key pair (original method)
            addr_index = data['address_index']
            key_index = data['key_index']
            
            if addr_index < 0 or addr_index >= len(address_list):
                return jsonify({"error": "Invalid address_index"}), 400
            
            if key_index < 0 or key_index >= len(key_list):
                return jsonify({"error": "Invalid key_index"}), 400
            
            address_data = address_list[addr_index]
            key_data = key_list[key_index]
            
            addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
            r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
            a_bytes = hex_to_bytes_safe(key_data['a_hex'])
            b_bytes = hex_to_bytes_safe(key_data['b_hex'])
            
            buf_size = get_element_size()
            q_sigma_buf = create_string_buffer(buf_size)
            h_buf = create_string_buffer(buf_size)
            dsk_buf = create_string_buffer(buf_size)
            
            for buf in [q_sigma_buf, h_buf, dsk_buf]:
                for i in range(buf_size):
                    buf[i] = 0
            
            lib.stealth_sign_simple(addr_bytes, r1_bytes, a_bytes, b_bytes, message_bytes,
                                   q_sigma_buf, h_buf, dsk_buf, buf_size)
            
            q_sigma_hex = bytes_to_hex_safe_fixed(q_sigma_buf, 'G1')
            h_hex = bytes_to_hex_safe_fixed(h_buf, 'Zr')
            dsk_hex = bytes_to_hex_safe_fixed(dsk_buf, 'G1')
            
            if not q_sigma_hex or not h_hex:
                raise Exception("Failed to sign message with key")
            
            return jsonify({
                "message": message,
                "q_sigma_hex": q_sigma_hex,
                "h_hex": h_hex,
                "dsk_hex": dsk_hex,
                "address_index": addr_index,
                "key_index": key_index,
                "address_id": address_data['id'],
                "key_id": key_data['id'],
                "method": "keypair",
                "status": "signed"
            })
        else:
            return jsonify({"error": "Please specify either dsk_index or (address_index and key_index)"}), 400
        
    except Exception as e:
        raise e

@app.route("/verify_signature", methods=["POST"])
def verify_signature():
    """Verify signature"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        required_fields = ['message', 'q_sigma_hex', 'h_hex', 'address_index']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing {field}"}), 400
        
        message = data['message']
        q_sigma_hex = data['q_sigma_hex']
        h_hex = data['h_hex']
        addr_index = data['address_index']
        
        if addr_index < 0 or addr_index >= len(address_list):
            return jsonify({"error": "Invalid address_index"}), 400
        
        address_data = address_list[addr_index]
        
        message_bytes = message.encode('utf-8')
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r2_bytes = hex_to_bytes_safe(address_data['r2_hex'])
        c_bytes = hex_to_bytes_safe(address_data['c_hex'])
        h_bytes = hex_to_bytes_safe(h_hex)
        q_sigma_bytes = hex_to_bytes_safe(q_sigma_hex)
        
        result = lib.stealth_verify_simple(addr_bytes, r2_bytes, c_bytes, message_bytes, h_bytes, q_sigma_bytes)
        
        return jsonify({
            "valid": bool(result),
            "message": message,
            "address_index": addr_index,
            "address_id": address_data['id'],
            "status": "verified" if result else "invalid"
        })
        
    except Exception as e:
        raise e

@app.route("/trace", methods=["POST"])
def trace_identity():
    """Trace identity for selected address"""
    try:
        ensure_initialized()
        
        data = request.get_json()
        if not data or 'address_index' not in data:
            return jsonify({"error": "Please specify address_index"}), 400
        
        addr_index = data['address_index']
        
        if addr_index < 0 or addr_index >= len(address_list):
            return jsonify({"error": "Invalid address_index"}), 400
        
        if trace_key is None:
            return jsonify({"error": "Trace key not initialized"}), 400
        
        address_data = address_list[addr_index]
        
        addr_bytes = hex_to_bytes_safe(address_data['addr_hex'])
        r1_bytes = hex_to_bytes_safe(address_data['r1_hex'])
        r2_bytes = hex_to_bytes_safe(address_data['r2_hex'])
        c_bytes = hex_to_bytes_safe(address_data['c_hex'])
        k_bytes = hex_to_bytes_safe(trace_key['k_hex'])
        
        buf_size = get_element_size()
        b_recovered_buf = create_string_buffer(buf_size)
        
        for i in range(buf_size):
            b_recovered_buf[i] = 0
        
        lib.stealth_trace_simple(addr_bytes, r1_bytes, r2_bytes, c_bytes, k_bytes,
                                b_recovered_buf, buf_size)
        
        b_recovered_hex = bytes_to_hex_safe_fixed(b_recovered_buf, 'G1')
        
        if not b_recovered_hex:
            raise Exception("Failed to trace identity")
        
        # Find matching key
        matched_key = None
        for i, key in enumerate(key_list):
            if key['B_hex'] == b_recovered_hex:
                matched_key = {
                    "index": i,
                    "id": key['id'],
                    "match": True
                }
                break
        
        return jsonify({
            "recovered_b_hex": b_recovered_hex,
            "address_index": addr_index,
            "address_id": address_data['id'],
            "original_owner": {
                "key_index": address_data['key_index'],
                "key_id": address_data['key_id'],
                "B_hex": address_data['owner_B']
            },
            "matched_key": matched_key,
            "perfect_match": matched_key is not None,
            "status": "traced"
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
    g1_size = 0
    zr_size = 0
    
    try:
        if system_initialized:
            g1_size = lib.stealth_element_size_G1()
            zr_size = lib.stealth_element_size_Zr()
    except:
        pass
    
    return jsonify({
        "initialized": system_initialized,
        "param_file": current_param_file,
        "trace_key_set": trace_key is not None,
        "keys_count": len(key_list),
        "addresses_count": len(address_list),
        "dsks_count": len(dsk_list),
        "g1_element_size": g1_size,
        "zr_element_size": zr_size,
        "library_loaded": True,
        "dsk_functions_available": DSK_FUNCTIONS_AVAILABLE,
        "architecture": "interactive_selectable_inputs"
    })

@app.route("/reset", methods=["POST"])
def reset_system():
    """Reset the system state"""
    global key_list, address_list, dsk_list, trace_key, system_initialized, current_param_file
    
    try:
        if system_initialized:
            lib.stealth_reset_performance()
        
        key_list.clear()
        address_list.clear()
        dsk_list.clear()
        trace_key = None
        system_initialized = False
        current_param_file = None
        
        return jsonify({
            "status": "reset complete",
            "message": "All system state has been reset"
        })
    except Exception as e:
        raise e

if __name__ == "__main__":
    print("🚀 Starting Interactive Stealth Demo Server")
    print("🎯 Features: Selectable inputs for all operations")
    print("💡 New: DSK generation, parameter file selection, flexible verification")
    print("🌐 Server will run on http://localhost:5000")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        if system_initialized:
            lib.stealth_cleanup()
            print("🧹 Library cleanup completed")