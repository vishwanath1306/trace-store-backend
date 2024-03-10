from flask import Flask
from pymilvus import connections, utility, CollectionSchema, DataType, FieldSchema, Collection

from utils.exceptions import MilvusConnectionError

class SemSearchMilvus(object):
    
    __slots__ = ['milvus_storage']
    
    def __init__(self) -> None:
        self.milvus_storage = None
    
    def establish_connection(self, app: Flask):
        try:
            connections.connect(alias="semantic_search", 
                    host=app.config['MILVUS_HOST'], 
                    port=app.config['MILVUS_PORT'])
        except Exception as e:
            raise MilvusConnectionError(f"Milvus connection failed due to: {e}")

milvus_conn = SemSearchMilvus()