import time
from typing import List
from datetime import datetime

from flask import current_app as app

from tasks import celery


from models.logtoembedding import LogToEmbedding
from models.status_kv import StatusKV
from models.session import SessionManager, EmbeddingMethod, VectorStore
from models.sessiontomilvus import PostgresToMilvus, PGMilvusSesssionConnect
from modules.integrations.google_integration import google_text_embedding

from services.milvus_service import milvus_conn

from utils.helpers import generate_id, read_file_content, get_all_json, read_json_file, collection_index_name_from_filename
from utils.parsers import get_parser_for_application


@celery.task(rate_limit='100/s')
def get_google_embedding(session_id: str, log_text: List[str]):
    return google_text_embedding(session_id, log_text)


@celery.task
def save_and_generate_embedding(session_id: str, log_file_path: str):

    session_details = SessionManager.get_session_details(session_id)
    log_text = read_file_content(log_file_path)
    
    current_status = StatusKV()
    current_status.create_new_session(session_id)

    check_if_completed.delay(session_id, len(log_text))

    application_name = session_details.application_name
    parser_function = get_parser_for_application(application_name)

    app.logger.info(f"Using parser for application: {application_name}")

    EMB_BATCH_SIZE = 128
    DB_WRITE_BATCH_SIZE = 128 * 10
    batch = []
    
    for idx in range(0, len(log_text), EMB_BATCH_SIZE):
        start, end = idx, min(idx + EMB_BATCH_SIZE, len(log_text))
        structured_logs = []
        embedding_lines = []
        for line in log_text[start:end]:
            structured_log, embedding_line = parser_function(line)
            structured_logs.append(structured_log)
            embedding_lines.append(embedding_line)

        if session_details.embedding_method == EmbeddingMethod.GOOGLE:
            embeddings = get_google_embedding(session_id, embedding_lines)

        for i, (structured_log, emb) in enumerate(zip(structured_logs, embeddings)):
            batch.append(LogToEmbedding(
                id=generate_id(),
                session_id=session_id,
                log_text=log_text[idx+i],
                embedding=emb,
                labels=structured_log['labels'],
                structured_metadata=structured_log['structured_metadata'],
                timestamp=datetime.fromisoformat(structured_log['timestamp'])
            ))
        
            if len(batch) >= DB_WRITE_BATCH_SIZE:
                batch[0].add_multiple_log_to_embedding(batch)
                StatusKV.increment_session_id_lines_completed(session_id, len(batch))
                batch = []
    
        if end == len(log_text) and batch:
            batch[0].add_multiple_log_to_embedding(batch)
            StatusKV.increment_session_id_lines_completed(session_id, len(batch))


    # for line in log_text:
    #     structured_log, embedding_line = parse_openstack_log_line(line)
    #     structured_logs.append(structured_log)
    #     embedding_lines.append(embedding_line)

    # if session_details.embedding_method == EmbeddingMethod.GOOGLE:
    #     embeddings = get_google_embedding(session_id, log_text)
    

    # for i, (structured_log, emb) in enumerate(zip(structured_logs, embeddings)):
    #     batch.append(LogToEmbedding(
    #         id=generate_id(),
    #         session_id=session_id,
    #         log_text=log_text[i],
    #         embedding=emb,
    #         labels=structured_log['labels'],
    #         structured_metadata=structured_log['structured_metadata'],
    #         timestamp=datetime.fromisoformat(structured_log['timestamp'])
    #     ))
        
    #     if len(batch) >= DB_WRITE_BATCH_SIZE:
    #         batch[0].add_multiple_log_to_embedding(batch)
    #         StatusKV.increment_session_id_lines_completed(session_id, len(batch))
    #         batch = []
    
    # if batch:
    #     batch[0].add_multiple_log_to_embedding(batch)
    #     StatusKV.increment_session_id_lines_completed(session_id, len(batch))


@celery.task
def write_embedding_to_db_milvus(session_id: str, file_name: str):
    
    file_data = read_json_file(file_name)
        
    log_lines = []    
    pg_milvus_session_connect_list: List[PGMilvusSesssionConnect] = []

    pg_to_milvus_id = generate_id()
    collection_name, index_name = collection_index_name_from_filename(file_name)
    pg_to_milvus = PostgresToMilvus(
        id=pg_to_milvus_id,
        collection_name=collection_name,
        index_name=index_name,
        session_id=session_id
    )
    pg_to_milvus.create_new_pg_milvus()
    print(f"Processing file: {file_name} with lines: {len(file_data)}")

    for data in file_data:

        log_to_embedding_id = generate_id()

        log_to_embedding = LogToEmbedding(
            id=log_to_embedding_id,
            session_id=session_id,
            log_text=data['text'],
            embedding=data['embedding']
        )

        pg_milvus_session_connect = PGMilvusSesssionConnect(
            id=generate_id(),
            session_id=session_id,
            log_to_embedding_id=log_to_embedding_id,
            pg_to_milvus_id=pg_to_milvus_id
        )
        
        log_lines.append(log_to_embedding)
        pg_milvus_session_connect_list.append(pg_milvus_session_connect)

    log_to_embedding.add_multiple_log_to_embedding(log_lines)
    pg_milvus_session_connect.add_multiple_pg_milvus_session_connect(pg_milvus_session_connect_list)

    StatusKV.increment_session_id_lines_completed(session_id)

@celery.task
def load_existing_embedding(session_id: str, folder_path: str):
    log_files = get_all_json(folder_path)
    current_session = SessionManager.get_session_details(session_id)
    print(f"Loading: {len(log_files)} files.")
    
    current_status = StatusKV()
    current_status.create_new_session(session_id)
    
    for file_ in log_files:
        if current_session.vector_store == VectorStore.MILVUS:
            write_embedding_to_db_milvus.delay(session_id, file_)

    check_if_completed.delay(session_id, len(log_files))

@celery.task
def check_if_completed(session_id: str, count_of_lines: int):
    
    while True:
        if StatusKV.get_lines_completed(session_id) == count_of_lines:
            print(f"Checking if completed: {count_of_lines}")
            session_manager = SessionManager.get_session_details(session_id)
            session_manager.update_status(True)
            StatusKV.delete_lines_completed(session_id)
            break
        time.sleep(5)

@celery.task
def load_into_milvus_collection(sesion_id: str):
    
    print("Loading into milvus collection")
    session_manager_object = SessionManager.get_session_details(sesion_id)
    pg_to_milvus_object = PostgresToMilvus.get_mutiple_pg_milvus(sesion_id)
    milvus_conn.establish_connection(app=app)
    '''
        First we get all the collection names for a particular session id. This can be done by querying the pg_to_milvus table. 
        --> Use this to create the collection. Get the field names for this as well. 

        Then we get all the log_to_embedding ids for a particular session id. This can be done by querying the pg_milvus_session_connect table.
        --> Split this into the various categories and then load it into the collection. 

        Put the various entities into the collection. 
    '''
    for pg_to_milvus in pg_to_milvus_object:
        print(f"Working with collection: {pg_to_milvus.collection_name} and index: {pg_to_milvus.index_name}")
        current_collection = milvus_conn.create_collection(
                collection_name=pg_to_milvus.collection_name, 
                description="Collection for session id: {session_id} to build index: {pg_to_milvus.index_name}",
            )

        pg_milvus_connect = PGMilvusSesssionConnect.get_all_pg_milvus_session_for_pg_milvus_id(pg_milvus_id=pg_to_milvus.id)
        log_id_list = [x.log_to_embedding_id for x in pg_milvus_connect]
        log_to_embedding_list = LogToEmbedding.get_log_to_embedding_milvus_format(log_id_list)
        milvus_conn.insert_data(
            collection=current_collection,
            entities=log_to_embedding_list
        )
        milvus_conn.create_index(current_collection, "embeddings", "IVF_FLAT", "L2", {"nlist": 768})    