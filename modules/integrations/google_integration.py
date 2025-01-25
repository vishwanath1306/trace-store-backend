from flask import current_app as app
from llama_index.embeddings.google import GooglePaLMEmbedding
from sentence_transformers import SentenceTransformer
from typing import List
from models.status_kv import StatusKV
import numpy as np

# def google_text_embedding(text: str):
#     embed_model = GooglePaLMEmbedding(model_name=app.config['GOOGLE_MODEL_NAME'], api_key=app.config['GOOGLE_API_KEY'])
#     return embed_model.get_text_embedding(text)




# def google_text_embedding(session_id: str, log_text: List[str]):
#     embed_model = SentenceTransformer('all-mpnet-base-v2', device='cuda')
#     # embed_model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
#     # print(f"Using device: {embed_model.device}")
    
#     batch_size = min(128, len(log_text))
#     total_batches = (len(log_text) + batch_size - 1) // batch_size
    
#     def update_progress(batch_num, _):
#         start_idx = batch_num * batch_size
#         current_batch_size = min(batch_size, len(log_text) - start_idx)
#         StatusKV.increment_session_id_lines_completed(session_id, current_batch_size)

#     embeddings = embed_model.encode(
#         log_text,
#         batch_size=batch_size
#         show_progress_bar=False,
#         callback=lambda batch: update_progress(batch, None))
    
#     return embeddings.astype(float).tolist()


def google_text_embedding(session_id: str, log_text: List[str]):
    embed_model = SentenceTransformer('all-mpnet-base-v2', device='cuda')
    
    batch_size = min(128, len(log_text))
    total_batches = (len(log_text) + batch_size - 1) // batch_size
    
    all_embeddings = []

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(log_text))

        batch_sentences = log_text[start_idx:end_idx]
        batch_embeddings = embed_model.encode(
            batch_sentences, 
            show_progress_bar=False
        )
        
        StatusKV.increment_session_id_lines_completed(session_id, len(batch_sentences))
        
        all_embeddings.append(batch_embeddings)
    
    if all_embeddings:
        embeddings_array = np.vstack(all_embeddings)
    else:
        embeddings_array = np.array([]).reshape(0,0)
    
    return embeddings_array.astype(float).tolist()
