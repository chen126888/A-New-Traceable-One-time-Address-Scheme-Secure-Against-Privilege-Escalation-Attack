from flask import request, jsonify
from app.api import bp

@bp.route('/transaction/create', methods=['POST'])
def create_transaction():
    return jsonify({"message": "Transaction API working"})
