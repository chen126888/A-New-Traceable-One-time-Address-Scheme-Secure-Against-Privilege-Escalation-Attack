from flask import Flask, jsonify, send_from_directory
from ctypes import *
import os

# 載入 libstealth.so
lib = CDLL("../lib/libstealth.so")
lib.stealth_setup.argtypes = [c_char_p]
lib.stealth_generate_addr.argtypes = [c_char_p, c_int]
lib.stealth_generate_addr.restype = c_int

# 初始化 pairing
lib.stealth_setup(b"../param/a.param")

app = Flask(__name__, static_folder="../frontend")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/addrgen", methods=["GET"])
def addrgen():
    buf = create_string_buffer(512)
    n = lib.stealth_generate_addr(buf, 512)
    if n <= 0:
        return jsonify({"error": "addrgen failed"}), 500

    addr_hex = buf.raw[:n].hex()
    return jsonify({"addr_hex": addr_hex})

if __name__ == "__main__":
    app.run(debug=True)
