import json
import logging
from copy import deepcopy
from functools import wraps
from typing import Dict, List, Tuple

from flask import request
from models.session import EmbeddingMethod, VectorStore
def verify_session_create(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        print(request.form)
        required_fields = ['session_name', 'vector_database', 'embedding_method']
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
