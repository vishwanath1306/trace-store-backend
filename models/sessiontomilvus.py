import datetime
import enum
from typing import Dict, Union, Tuple

from flask import current_app as app
from sqlalchemy.exc import IntegrityError

from models import database

class PostgresToMilvus(database.Model):
    
    __tablename__ = 'postgres_to_milvus'

    id = database.Column(database.String(128), primary_key=True, nullable=False)
    collection_name = database.Column(database.String(128), nullable=False)
    index_name = database.Column(database.String(128), nullable=False)

    session_id = database.Column(database.String(128), database.ForeignKey('session_manager.id'), nullable=False)

    created_at = database.Column(database.DateTime, default=datetime.datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, id, collection_name, index_name, session_id):
        self.id = id
        self.collection_name = collection_name
        self.index_name = index_name
        self.session_id = session_id
    
    def create_new_pg_milvus(self):
        try:
            database.session.add(self)
            database.session.commit()
        except IntegrityError as e:
            from utils.helpers import extract_sqlalchemy_errors
            database.session.rollback()
            message: str = f"PostgresToMilvus: {extract_sqlalchemy_errors(e._message)}"
            message_dict = {
                "message": message
            }
            return False, message_dict

        message_dict = {
            "message": "Postgres to Milvus created successfully"
        }
        return True, message_dict
    
    