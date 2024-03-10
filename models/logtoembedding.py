import datetime
import enum
from typing import Dict, Union, Tuple

from flask import current_app as app
from sqlalchemy.exc import IntegrityError

from models import database

class LogToEmbedding(database.Model):

    __tablename__ = 'log_to_embedding'

    id = database.Column(database.String(128), primary_key=True, nullable=False)
    log_text = database.Column(database.String(1024), nullable=False)
    embedding = database.Column(database.ARRAY(database.Float), nullable=False)

    session_id = database.Column(database.String(128), database.ForeignKey('session_manager.id'), nullable=False)

    created_at = database.Column(database.DateTime, default=datetime.datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, id: str, log_text: str, embedding: str, session_id: str) -> None:
        self.id = id
        self.log_text = log_text
        self.embedding = embedding
        self.session_id = session_id
    

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