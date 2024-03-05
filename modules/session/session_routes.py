from typing import Dict

from flask import Blueprint, request, jsonify
from flask import current_app as app

from models.session import SessionManager
from modules.session.composed import verify_session_create
from utils.helpers import generate_id, store_file


session_bp = Blueprint('session_bp', __name__, url_prefix='/api/v1/session')

@session_bp.route('/session-hw', methods=['GET'])
def session_hw():
    return jsonify({'message': 'Hello, World!'})

@session_bp.route('/create', methods=['POST'])
@verify_session_create
def create_session(session_details: Dict):
    sess_id = generate_id()
    file_name = f"{app.config['TEMP_FILE_UPLOAD_FOLDER']}/{sess_id}.log"
    session_manager = SessionManager(
        id=sess_id,
        name=session_details['session_name'],
        vector_store=session_details['vector_database'],
        embedding_method=session_details['embedding_method'],
        log_file_path=file_name
    )
    store_file(session_details['request_file'], file_name)
    value, message = session_manager.create_new_user()
    if not value:
        return jsonify({'message': message['message']}), 400
    else:
        return jsonify({'message': message['message']}), 201
