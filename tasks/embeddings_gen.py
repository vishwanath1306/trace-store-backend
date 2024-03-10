import time

from tasks import celery

from models.logtoembedding import LogToEmbedding
from models.status_kv import StatusKV
from models.session import SessionManager, VectorStore, EmbeddingMethod
from modules.integrations.google_integration import google_text_embedding

from utils.helpers import generate_id, read_file_content, get_all_json, read_json_file


@celery.task(rate_limit='10/s')
def get_google_embedding(session_id: str, text_line: str):
    embedding_text = google_text_embedding(text_line)
    StatusKV.increment_session_id_lines_completed(session_id)
    log_to_embedding = LogToEmbedding(
        id=generate_id(),
        session_id=session_id,
        log_text=text_line,
        embedding=embedding_text
    )
    _ = log_to_embedding.create_new_log_to_embedding()

@celery.task
def save_and_generate_embedding(session_id: str, log_file_path: str):
    session_details = SessionManager.get_session_details(session_id)
    log_text = read_file_content(log_file_path)
    
    current_status = StatusKV()
    current_status.create_new_session(session_id)

    check_if_completed.delay(session_id, len(log_text))

    if session_details.embedding_method == EmbeddingMethod.GOOGLE:
        for line in log_text:
            get_google_embedding.delay(session_id, line)
            time.sleep(1)

    
@celery.task
def generate_for_vector_store(session_id: str, log_file_path: str):
    pass


@celery.task
def write_embedding_to_db(session_id: str, file_name: str):
    file_data = read_json_file(file_name)
    for data in file_data:
        log_to_embedding = LogToEmbedding(
            id=generate_id(),
            session_id=session_id,
            log_text=data['text'],
            embedding=data['embedding']
        )
        log_to_embedding.create_new_log_to_embedding()


@celery.task
def manual_embedding_generation(session_id: str, folder_path: str):
    log_files = get_all_json(folder_path)
    for file_ in log_files:
        write_embedding_to_db.delay(session_id, file_)


@celery.task
def check_if_completed(session_id: str, count_of_lines: int):
    
    while True:
        if StatusKV.get_lines_completed(session_id) == count_of_lines:
            print(f"Checking if completed: {count_of_lines}")
            session_manager = SessionManager.get_session_details(session_id)
            session_manager.update_status(True)
            StatusKV.delete_lines_completed(session_id)
            break
