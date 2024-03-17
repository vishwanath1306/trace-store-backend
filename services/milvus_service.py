from flask import Flask
from pymilvus import connections, utility, CollectionSchema, DataType, FieldSchema, Collection

from utils.exceptions import MilvusConnectionError

class SemSearchMilvus(object):
    
    __slots__ = ['milvus_storage']
    
    def __init__(self) -> None:
        self.milvus_storage = None
    
    def establish_connection(self, app: Flask):
        try:
            connections.connect(alias="default", 
                    host=app.config['MILVUS_HOST'], 
                    port=app.config['MILVUS_PORT'])
        except Exception as e:
            raise MilvusConnectionError(f"Milvus connection failed due to: {e}")
        
    def get_default_fields(self):
        fields = [
            FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=128),
            FieldSchema(name="log_line", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=768)
        ]
        return fields

    def create_collection(self, collection_name, description, consistency_level="Strong"):
        schema = CollectionSchema(fields=self.get_default_fields(), description=description)
        collection = Collection(name=collection_name, schema=schema, consistency_level=consistency_level)
        return collection
    
    def insert_data(self, collection, entities):
        ins_data = collection.insert(entities)
        collection.flush()
        return ins_data
    
    def create_index(self, collection, field_name, index_type, metric_type, params):
        index = {
            "index_type": index_type,
            "metric_type": metric_type,
            "params": params
        }
        collection.create_index(field_name, index)
        print(f"Created index on {field_name} for collection: {collection.name}")

    def search_and_query(self, collection, search_vectors, limit, search_field, search_params):
        collection.load()
        results = collection.search(
            search_vectors, search_field, search_params, limit=limit, output_fields=["log_line"])

        return results
    
    def delete_collection(collection):
        collection.drop()
        print(f"Deleted collection: {collection.name}")

    def delete_entities(collection, expr):
        collection.delete(expr)
        print(f"Deleted entities where {expr}")

    def drop_collection(self, collection_name):
        utility.drop_collection(collection_name)
        return True
    
    def get_collection(self, collection_name: str):
        return Collection(collection_name)
    
    def get_log_lines(self, results):
        log_line = []
        for hits in results:
            for hit in hits:
                log_line.append(hit.entity.get('log_line'))
        return log_line
    
milvus_conn = SemSearchMilvus()