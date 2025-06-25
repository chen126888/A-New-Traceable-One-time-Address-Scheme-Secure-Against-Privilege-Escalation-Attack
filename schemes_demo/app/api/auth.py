from flask import request, jsonify
from app.api import bp

@bp.route('/auth/test', methods=['GET'])
def auth_test():
    return jsonify({"message": "Auth API working"})
