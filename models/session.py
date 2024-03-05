import datetime
import enum
from typing import Dict, Union, Tuple

from flask import current_app as app
from sqlalchemy.exc import IntegrityError

from models import database
from utils.exceptions import SessionNotFoundException

class ExampleTable(database.Model):
    __tablename__ = 'example_table'
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), nullable=False)
    created_at = database.Column(database.DateTime, default=datetime.datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, id, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return f'<ExampleTable {self.name}>'

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class EmbeddingMethod(enum.Enum):
    GOOGLE = 'Google'
    OPENAI = 'OpenAI'

class VectorStore(enum.Enum):
    MILVUS = 'Milvus'
    FAISS = 'Faiss'
    WEVIATE = 'Weaviate'


class SessionManager(database.Model):
    __tablename__ = 'session_manager'

    id = database.Column(database.String(128), primary_key=True, nullable=False)
    created_at = database.Column(database.DateTime, default=datetime.datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    name = database.Column(database.String(128), nullable=False)
    log_file_path = database.Column(database.String(256), nullable=False)
    vector_store = database.Column(database.Enum(VectorStore), nullable=False)
    embedding_method = database.Column(database.Enum(EmbeddingMethod), nullable=False)

    created_at = database.Column(database.DateTime, default=datetime.datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, id: str, name: str, log_file_path: str, vector_store: VectorStore, embedding_method: EmbeddingMethod):
        self.id = id
        self.name = name
        self.log_file_path = log_file_path
        self.vector_store = vector_store
        self.embedding_method = embedding_method
    
    def create_new_user(self) -> Tuple[bool, Dict]:
        try: 
            database.session.add(self)
            database.session.commit()
        except IntegrityError as e:
            from utils.helpers import extract_sqlalchemy_errors
            database.session.rollback()
            message: str = f"Session: {extract_sqlalchemy_errors(e._message)}"
            message_dict = {
                "message": message
            }
            return False, message_dict
        message_dict = {
            "message": "Session created successfully"
        }
        return True, message_dict