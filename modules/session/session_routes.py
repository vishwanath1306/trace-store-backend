from flask import Blueprint, request, jsonify

session_bp = Blueprint('session_bp', __name__, url_prefix='/api/v1/session')

@session_bp.route('/session-hw', methods=['GET'])
def session_hw():
    return jsonify({'message': 'Hello, World!'})