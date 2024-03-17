import datetime
import enum
from typing import Dict, Union, Tuple

from flask import current_app as app
from sqlalchemy.exc import IntegrityError

from models import database

from services.milvus_service import milvus_conn, SemSearchMilvus

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

    def add_multiple_postgres_to_milvus(self, postgres_to_milvus_list):
        database.session.add_all(postgres_to_milvus_list)
        database.session.commit()

    @staticmethod
    def get_mutiple_pg_milvus(session_id):
        return PostgresToMilvus.query.filter_by(session_id=session_id).all()
    
    def drop_milvus_collection(self):
        milvus_conn.drop_collection(self.collection_name)
        return True

    @staticmethod
    def get_collection_for_session_collection_name(session_id, collection_name):
        return PostgresToMilvus.query.filter_by(session_id=session_id, collection_name=collection_name).first()

class PGMilvusSesssionConnect(database.Model):

    __tablename__ = 'pg_milvus_session_connect'

    id = database.Column(database.String(128), primary_key=True, nullable=False)
    session_id = database.Column(database.String(128), database.ForeignKey('session_manager.id'), nullable=False)
    log_to_embedding_id = database.Column(database.String(128), database.ForeignKey('log_to_embedding.id'), nullable=False)
    pg_to_milvus_id = database.Column(database.String(128), database.ForeignKey('postgres_to_milvus.id'), nullable=False)

    def __init__(self, id, session_id, log_to_embedding_id, pg_to_milvus_id):
        self.id = id
        self.session_id = session_id
        self.log_to_embedding_id = log_to_embedding_id
        self.pg_to_milvus_id = pg_to_milvus_id
    
    def create_new_pg_milvus_session_connect(self):
        try:
            database.session.add(self)
            database.session.commit()
        except IntegrityError as e:
            from utils.helpers import extract_sqlalchemy_errors
            database.session.rollback()
            message: str = f"PGMilvusSesssionConnect: {extract_sqlalchemy_errors(e._message)}"
            message_dict = {
                "message": message
            }
            return False, message_dict

        message_dict = {
            "message": "PGMilvusSesssionConnect created successfully"
        }
        return True, message_dict

    def add_multiple_pg_milvus_session_connect(self, pg_milvus_session_connect_list):
        database.session.add_all(pg_milvus_session_connect_list)
        database.session.commit()
    
    @staticmethod
    def get_pg_milvus_session_with_limit(limit: int):
        return PGMilvusSesssionConnect.query.limit(limit).all()
    
    @staticmethod
    def get_all_pg_milvus_session():
        return PGMilvusSesssionConnect.query.all()
    
    @staticmethod
    def get_all_pg_milvus_session_for_pg_milvus_id(pg_milvus_id):
        return PGMilvusSesssionConnect.query.filter_by(pg_to_milvus_id=pg_milvus_id).all()
    