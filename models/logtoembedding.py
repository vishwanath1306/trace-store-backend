import datetime
import enum
from typing import Dict, Union, Tuple, List

from flask import current_app as app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector

from models import database

class LogToEmbedding(database.Model):

    __tablename__ = 'log_to_embedding'

    id = database.Column(database.String(128), primary_key=True, nullable=False)
    log_text = database.Column(database.String(1024), nullable=False)
    embedding = database.Column(Vector(768), nullable=False)
    
    # New columns for structured data
    labels = database.Column(database.JSON, nullable=False)
    structured_metadata = database.Column(database.JSON, nullable=True)
    timestamp = database.Column(database.DateTime, nullable=False)
    
    session_id = database.Column(database.String(128), database.ForeignKey('session_manager.id'), nullable=False)

    created_at = database.Column(database.DateTime, default=datetime.datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, id: str, log_text: str, embedding: List[float], session_id: str, 
                 labels: Dict, structured_metadata: Dict, timestamp: datetime):
        self.id = id
        self.log_text = log_text
        self.embedding = embedding
        self.session_id = session_id
        self.labels = labels
        self.structured_metadata = structured_metadata
        self.timestamp = timestamp
    

    def create_new_log_to_embedding(self): 
        try: 
            database.session.add(self)
            database.session.commit()
        except IntegrityError as e:
            from utils.helpers import extract_sqlalchemy_errors
            database.session.rollback()
            message: str = f"LogToEmbedding: {extract_sqlalchemy_errors(e._message)}"
            message_dict = {
                "message": message
            }
            return False, message_dict

        message_dict = {
            "message": "Log to embedding created successfully"
        }
        return True, message_dict

    @staticmethod
    def cosine_similarity_search(query_embedding: List[float], limit: int = 10):
        results = (LogToEmbedding.query
        .with_entities(
            LogToEmbedding,
            LogToEmbedding.embedding.cosine_distance(query_embedding).label('similarity')
        )
        .order_by(LogToEmbedding.embedding.cosine_distance(query_embedding))
        .limit(limit)
        .all())
    
        # Add similarity score to each LogToEmbedding object
        for log, similarity in results:
            log.similarity = 1 - similarity  # Convert distance to similarity score
        
        # Return just the LogToEmbedding objects with similarity scores attached
        return [log for log, _ in results]
    
    @staticmethod
    def l2_distance_search(query_embedding: List[float], limit: int = 10):
        results = (LogToEmbedding.query
                .with_entities(
                    LogToEmbedding,
                    LogToEmbedding.embedding.l2_distance(query_embedding).label('distance')
                )
                .order_by(LogToEmbedding.embedding.l2_distance(query_embedding))
                .limit(limit)
                .all())
        
        # Add distance score to each LogToEmbedding object
        for log, distance in results:
            log.similarity = 1.0 - distance 
        
        # Return just the LogToEmbedding objects with distance scores attached
        return [log for log, _ in results]


    def add_multiple_log_to_embedding(self, log_to_embedding_list: List['LogToEmbedding']):
        try:
            database.session.add_all(log_to_embedding_list)
            database.session.commit()
        except IntegrityError as e:
            from utils.helpers import extract_sqlalchemy_errors
            database.session.rollback()
            message: str = f"LogToEmbedding Batch: {extract_sqlalchemy_errors(e._message)}"
            message_dict = {
                "message": message
            }
            return False, message_dict
        except Exception as e:
            database.session.rollback()
            message_dict = {
                "message": f"Unexpected error during batch insert: {str(e)}"
            }
            return False, message_dict

        message_dict = {
            "message": f"Successfully inserted {len(log_to_embedding_list)} log embeddings"
        }
        return True, message_dict
    
    @staticmethod
    def get_log_to_embedding(lte_id: str):

        return database.session.query(LogToEmbedding).filter_by(id=lte_id).first()

    # @staticmethod
    # def get_log_to_embedding_milvus_format(lte_ids: List[str]):
    #     log_lines = database.session.query(LogToEmbedding).filter(LogToEmbedding.id.in_(lte_ids)).all()
    #     return_list = [ [], [], []]
    #     for idx, log in enumerate(log_lines):
    #         return_list[0].append(str(idx+1))
    #         return_list[1].append(log.log_text)
    #         return_list[2].append(log.embedding)
    #     return return_list