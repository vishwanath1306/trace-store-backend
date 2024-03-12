import datetime
import enum
from typing import Dict, Union, Tuple

from flask import current_app as app
from sqlalchemy.exc import IntegrityError

from models import database
from utils.exceptions import SessionNotFoundException

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
    vector_store = database.Column(database.Enum(VectorStore), nullable=False)
    embedding_method = database.Column(database.Enum(EmbeddingMethod), nullable=False)
    application_name = database.Column(database.String(128), nullable=False)
    current_status = database.Column(database.Boolean, default=False)

    created_at = database.Column(database.DateTime, default=datetime.datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, id: str, name: str, vector_store: VectorStore, embedding_method: EmbeddingMethod, application_name: str):
        self.id = id
        self.name = name
        self.vector_store = vector_store
        self.embedding_method = embedding_method
        self.current_status = False
        self.application_name = application_name

    def create_new_session(self) -> Tuple[bool, Dict]:
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
    
    @staticmethod
    def get_folder_path(session_id: str) -> str:
        folder_path = SessionManager.query.filter_by(id=session_id).first()
        if folder_path is None:
            raise SessionNotFoundException("Session not found")
        
        return folder_path.to_dict()['log_file_path']
    
    @staticmethod
    def get_session_details(session_id: str) -> Union['SessionManager', None]:
        session = SessionManager.query.filter_by(id=session_id).first()

        if session is None:
            raise SessionNotFoundException("Session not found")
        return session
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'vector_store': self.vector_store.value,
            'embedding_method': self.embedding_method.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def update_status(self, status: bool) -> None:
        self.current_status = status
        
        try:             
            database.session.commit()
            
        except IntegrityError as e:
            from utils.helpers import extract_sqlalchemy_errors
            database.session.rollback()
            message: str = f"Session: {extract_sqlalchemy_errors(e._message)}"
            message_dict = {
                "message": message
            }
            return False, message_dict

    @staticmethod
    def check_session_details(session_id):
        session = SessionManager.query.filter_by(id=session_id).first()
        if session: 
            return True
        else:
            return False
    
    @staticmethod
    def check_session_status(session_id):
        session = SessionManager.query.filter_by(id=session_id).first()
        if session:
            return session.current_status

    @staticmethod
    def get_all_session():
        sessions = SessionManager.query.all()
        sessions_list = []
        for session in sessions:
            sessions_list.append(session.to_dict())
        return sessions_list