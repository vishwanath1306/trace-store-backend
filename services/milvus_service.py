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

    def get_default_fields(self):
        fields = [
            FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=128),
            FieldSchema(name="log_line", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=768)
        ]
        return fields

    def create_collection(collection_name, fields, description, consistency_level="Strong"):
        schema = CollectionSchema(fields=fields, description=description)
        collection = Collection(name=collection_name, schema=schema, consistency_level=consistency_level)
        return collection
    
    def insert_data(collection, entities):
        ins_data = collection.insert(entities)
        collection.flush()
        print(
            f"Inserted data into: {collection.name}. \nNumber of entities inserted: {collection.num_entities}"
        )
        return ins_data
    
    def create_index(collection, field_name, index_type, metric_type, params):
        index = {
            "index_type": index_type,
            "metric_type": metric_type,
            "params": params
        }
        collection.create_index(field_name, index)
        print(f"Created index on {field_name} for collection: {collection.name}")

    def search_and_query(collection, search_vectors, search_field, search_params):
        collection.load()

        results = collection.search(
            search_vectors, search_field, search_params, limit=10, output_fields=["log_line"])
    
    def delete_collection(collection):
        collection.drop()
        print(f"Deleted collection: {collection.name}")

    def delete_entities(collection, expr):
        collection.delete(expr)
        print(f"Deleted entities where {expr}")

    def drop_collection(collection_name):
        utility.drop_collection(collection_name)
        print(f"Dropped collection '{collection_name}'.")
        
milvus_conn = SemSearchMilvus()