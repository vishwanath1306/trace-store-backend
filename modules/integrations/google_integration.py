from flask import current_app as app
from llama_index.embeddings.google import GooglePaLMEmbedding

def google_text_embedding(text: str):
    embed_model = GooglePaLMEmbedding(model_name=app.config['GOOGLE_MODEL_NAME'], api_key=app.config['GOOGLE_API_KEY'])
    return embed_model.get_text_embedding(text)
