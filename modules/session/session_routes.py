from typing import Dict

from flask import Blueprint, request, jsonify
from flask import current_app as app

from models.session import SessionManager
from models.status_kv import StatusKV
from modules.session.composed import verify_session_create, verify_manual_embedding_generation

from tasks.embeddings_gen import save_and_generate_embedding, load_existing_embedding

from utils.exceptions import SessionNotFoundException
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
        application_name=session_details['application_name']
    )

    store_file(session_details['request_file'], file_name)
    value, message = session_manager.create_new_session()
    save_and_generate_embedding.delay(sess_id, f"{app.config['TEMP_FILE_UPLOAD_FOLDER']}/{sess_id}.log")

    if not value:
        return jsonify({'message': message['message']}), 400
    else:
        message_dict = {
            "message": message['message'],
            "session_id": sess_id
        }
        return jsonify(message_dict), 201


@session_bp.route('/details', methods=['GET'])
def get_session_details():
    sess_id = request.args.get('session_id')
    try:
        session_manager = SessionManager.get_session_details(sess_id)
    except SessionNotFoundException:
        return jsonify({'message': 'Session not found'}), 404
    return jsonify(session_manager.to_dict()), 200


@session_bp.route('/current-status', methods=['GET'])
def get_current_status():
    sess_id = request.args.get('session_id')
    sess_exists = SessionManager.check_session_status(sess_id)
    if sess_exists:
        message_dict = {
            "session_id": sess_id,
            "status": True,
            "message": "Index created"
        }
        return jsonify(message_dict), 200
    else:
        message_dict = {
            "session_id": sess_id,
            "status": False,
            "message": "Index construction in progress"
        }
        return jsonify(message_dict), 200


@session_bp.route('/manual-embedding-generation', methods=['POST'])
@verify_manual_embedding_generation
def manual_embedding_generation(session_details: Dict):
    sess_id = generate_id()
    session_manager = SessionManager(
        id=sess_id,
        name=session_details['session_name'],
        vector_store=session_details['vector_database'],
        embedding_method=session_details['embedding_method'],
        application_name=session_details['application_name'],
    )
    path_value = f"{app.config['EMBEDDING_FOLDER']}/{session_details['app_to_embedding']}/"
    
    
    
    value, message = session_manager.create_new_session()

    load_existing_embedding.delay(sess_id, path_value)

    if not value:
        return jsonify({'message': message['message']}), 400
    else:
        message_dict = {
            "message": message['message'],
            "session_id": sess_id
        }
        return jsonify(message_dict), 201
