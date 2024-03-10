import json
import logging
from copy import deepcopy
from functools import wraps
from typing import Dict, List, Tuple

from flask import request
from models.session import EmbeddingMethod, VectorStore
from models.session import SessionManager

def verify_session_create(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        required_fields = ['session_name', 'vector_database', 'embedding_method', 'application_name']
        file_field = 'request_file'
        session_details = {}
        for field in required_fields:
            session_details[field] = request.form.get(field, None)
            if session_details[field] is None:
                return {'message': f'{field} is required'}, 400
        if file_field not in request.files:
            return {'message': f'{file_field} is required'}, 400
        session_details[file_field] = request.files[file_field]

        session_details['vector_database'] = VectorStore(session_details['vector_database'])
        session_details['embedding_method'] = EmbeddingMethod(session_details['embedding_method'])

        return func(session_details=session_details)
    return decorated_function


def verify_session_validity(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        session_id = request.args.get('session_id')
        session_exists = SessionManager.check_session_details(session_id)
        if session_exists:
            return func(session_id=session_id)
        else:
            return func(session_id=False)
    return decorated_function


def verify_manual_embedding_generation(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        required_fields = ['session_name', 'vector_database', 'embedding_method', 'application_name']
        request_body = request.get_json()
        session_details = {}
        for field in request_body:
            session_details[field] = request_body.get(field, None)
            if session_details[field] is None:
                return {'message': f'{field} is required'}, 400
        session_details['vector_database'] = VectorStore(session_details['vector_database'])
        session_details['embedding_method'] = EmbeddingMethod(session_details['embedding_method'])
        return func(session_details=session_details)
    return decorated_function