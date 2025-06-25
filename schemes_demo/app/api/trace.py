from flask import request, jsonify
from app.api import bp

@bp.route('/trace/identity', methods=['POST'])
def trace_identity():
    return jsonify({"message": "Trace API working"})
