from flask import Flask, request, jsonify
from flask import send_from_directory
from ctypes import *
import os

lib = CDLL("../lib/libstealth.so")
lib.stealth_setup(b"../param/a.param")

# Setup argument types
lib.stealth_setup.argtypes = [c_char_p]
lib.stealth_generate_addr.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
lib.stealth_generate_addr.restype = c_int
lib.stealth_addr_verify.argtypes = [c_char_p, c_char_p, c_char_p]
lib.stealth_addr_verify.restype = c_int
lib.stealth_fast_addr_verify.argtypes = [c_char_p, c_char_p]
lib.stealth_fast_addr_verify.restype = c_int
lib.stealth_dskgen.argtypes = [c_char_p, c_char_p, c_char_p, c_int]
lib.stealth_dskgen.restype = c_int
lib.stealth_sign.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
lib.stealth_sign.restype = c_int
lib.stealth_verify.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
lib.stealth_verify.restype = c_int
lib.stealth_trace.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
lib.stealth_trace.restype = c_int

app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')


@app.route("/addrgen", methods=["GET"])
def addrgen():
    buf_addr = create_string_buffer(512)
    buf_r1   = create_string_buffer(512)
    buf_r2   = create_string_buffer(512)
    buf_c    = create_string_buffer(512)

    n = lib.stealth_generate_addr(buf_addr, buf_r1, buf_r2, buf_c, 512)
    if n <= 0:
        return jsonify({"error": "generation failed"}), 500

    return jsonify({
        "addr_hex": buf_addr.raw[:n].hex(),
        "r1_hex": buf_r1.raw[:n].hex(),
        "r2_hex": buf_r2.raw[:n].hex(),
        "c_hex":  buf_c.raw[:n].hex()
    })

@app.route("/dskgen", methods=["POST"])
def dskgen():
    data = request.get_json()
    addr = bytes.fromhex(data['addr'])
    r1 = bytes.fromhex(data['r1'])
    out = create_string_buffer(512)
    n = lib.stealth_dskgen(addr, r1, out, 512)
    if n <= 0:
        return jsonify({"error": "dskgen failed"}), 500
    return jsonify({"dsk_hex": out.raw[:n].hex()})

@app.route("/addrverify", methods=["POST"])
def addrverify():
    data = request.get_json()
    addr = bytes.fromhex(data['addr'])
    r1 = bytes.fromhex(data['r1'])
    c = bytes.fromhex(data['c'])
    res = lib.stealth_addr_verify(addr, r1, c)
    return jsonify({"valid": bool(res)})

@app.route("/fastaddrverify", methods=["POST"])
def fastaddrverify():
    data = request.get_json()
    r1 = bytes.fromhex(data['r1'])
    c = bytes.fromhex(data['c'])
    res = lib.stealth_fast_addr_verify(r1, c)
    return jsonify({"valid": bool(res)})

@app.route("/sign", methods=["POST"])
def sign():
    data = request.get_json()
    addr = bytes.fromhex(data['addr'])
    dsk = bytes.fromhex(data['dsk'])
    msg = data['msg'].encode()
    Q_buf = create_string_buffer(512)
    h_buf = create_string_buffer(512)
    lib.stealth_sign(Q_buf, h_buf, addr, dsk, msg)
    return jsonify({
        "Q_sigma": Q_buf.raw.hex(),
        "hZ": h_buf.raw.hex()
    })

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    addr = bytes.fromhex(data['addr'])
    r2 = bytes.fromhex(data['r2'])
    c = bytes.fromhex(data['c'])
    h = bytes.fromhex(data['h'])
    q = bytes.fromhex(data['q'])
    msg = data['msg'].encode()
    res = lib.stealth_verify(addr, r2, c, msg, h, q)
    return jsonify({"valid": bool(res)})

@app.route("/trace", methods=["POST"])
def trace():
    data = request.get_json()
    addr = bytes.fromhex(data['addr'])
    r1 = bytes.fromhex(data['r1'])
    r2 = bytes.fromhex(data['r2'])
    c = bytes.fromhex(data['c'])
    out = create_string_buffer(512)
    n = lib.stealth_trace(addr, r1, r2, c, out, 512)
    if n <= 0:
        return jsonify({"error": "trace failed"}), 500
    return jsonify({"B_r": out.raw[:n].hex()})

if __name__ == "__main__":
    app.run(debug=True)
