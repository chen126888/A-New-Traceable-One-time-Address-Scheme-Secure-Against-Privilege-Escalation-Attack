from flask import Flask, request, jsonify, send_from_directory
from ctypes import *
import os

lib = CDLL("../lib/libstealth.so")
lib.stealth_setup(b"../param/a.param")

lib.stealth_setup.argtypes = [c_char_p]
lib.stealth_keygen.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
lib.stealth_keygen.restype = None
lib.stealth_tracekeyget.argtypes = [c_char_p, c_char_p, c_int]
lib.stealth_tracekeyget.restype = None
lib.stealth_generate_addr.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
lib.stealth_generate_addr.restype = None

key_list = []
trace_key = None

app = Flask(__name__, static_folder="frontend")

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/setup", methods=["GET"])
def setup():
    global trace_key
    lib.stealth_setup(b"../param/a.param")
    TK = create_string_buffer(512)
    k  = create_string_buffer(512)
    lib.stealth_tracekeyget(TK, k, 512)
    trace_key = {
        "TK_hex": TK.raw.hex(),
        "k_hex": k.raw.hex()
    }
    return jsonify({"status": "setup complete", **trace_key})

@app.route("/keygen", methods=["GET"])
def keygen():
    A = create_string_buffer(512)
    B = create_string_buffer(512)
    a = create_string_buffer(512)
    b = create_string_buffer(512)
    lib.stealth_keygen(A, B, a, b, 512)
    item = {
        "index": len(key_list),
        "A_hex": A.raw.hex(),
        "B_hex": B.raw.hex(),
        "a_hex": a.raw.hex(),
        "b_hex": b.raw.hex()
    }
    key_list.append(item)
    return jsonify(item)

@app.route("/keylist", methods=["GET"])
def keylist():
    return jsonify(key_list)

@app.route("/tracekey", methods=["GET"])
def tracekey():
    if trace_key is None:
        return jsonify({"error": "trace key not yet generated"}), 404
    return jsonify(trace_key)

@app.route("/addrgen", methods=["POST"])
def addrgen():
    data = request.get_json()
    A = bytes.fromhex(data['A_hex'])
    B = bytes.fromhex(data['B_hex'])
    TK = bytes.fromhex(trace_key['TK_hex']) if trace_key else None

    if TK is None:
        return jsonify({"error": "trace key not initialized"}), 400

    buf_addr = create_string_buffer(512)
    buf_r1   = create_string_buffer(512)
    buf_r2   = create_string_buffer(512)
    buf_c    = create_string_buffer(512)

    lib.stealth_generate_addr(A, B, TK, buf_addr, buf_r1, buf_r2, buf_c, 512)

    return jsonify({
        "addr_hex": buf_addr.raw.hex(),
        "r1_hex": buf_r1.raw.hex(),
        "r2_hex": buf_r2.raw.hex(),
        "c_hex":  buf_c.raw.hex()
    })

if __name__ == "__main__":
    app.run(debug=True)
