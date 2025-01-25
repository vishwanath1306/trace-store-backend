import json
import logging
from copy import deepcopy
from functools import wraps
from typing import Dict, List, Tuple

from flask import request
from models.session import EmbeddingMethod, VectorStore
from models.session import SessionManager
from models.sessiontomilvus import PGMilvusSesssionConnect, PostgresToMilvus

from modules.integrations.google_integration import google_text_embedding

from services.milvus_service import SemSearchMilvus, milvus_conn
from services.openai_service import call_openai_api_log_file, convert_to_prompt_base, convert_to_prompt_ipaddr, convert_to_prompt_user
from utils.helpers import construct_app_to_embedding, collection_index_name_from_filename

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
        session_details['app_to_embedding'] = construct_app_to_embedding(str.lower(session_details['application_name']), str.lower(session_details['embedding_method'].value))
        
        return func(session_details=session_details)
    return decorated_function

def query_logs_and_api_call(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        request_data = request.get_json()
        session_id = request_data.get('session_id')
        query_string = request_data.get('query_string')
        
        query_embedding = google_text_embedding(query_string)
        
        from models.logtoembedding import LogToEmbedding
        similar_logs = LogToEmbedding.cosine_similarity_search(query_embedding, limit=10)
        
        final_log_lines = []
        for log in similar_logs:
            final_log_lines.append({
                "log_text": log.log_text,
                "similarity": float(log.similarity),
                "created_at": log.created_at.isoformat()
            })

        # Process with OpenAI if needed
        final_result_values = []
        # if final_log_lines:
        #     prompt_text = convert_to_prompt_base([log["log_text"] for log in final_log_lines])
        #     extracted_log_lines = call_openai_api_log_file(prompt_text)
            
        #     prompt_text_2 = convert_to_prompt_ipaddr(extracted_log_lines, query_string)
        #     final_result_values.append(call_openai_api_log_file(prompt_text_2))

        return_dict = {
            "log_lines": final_log_lines,
            "result_value": final_result_values
        }

        return func(return_dict)
    return decorated_function