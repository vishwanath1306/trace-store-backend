from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from typing import List

app = Flask(__name__)

# Load the model globally so it's only loaded once
# model = SentenceTransformer('ishandotsh/logembed_a1', device='cuda')
# model = SentenceTransformer('../embeddinglogs/models/logembed_a2_20250302_205530/', device='cuda')
model = SentenceTransformer('../embeddinglogs/models/logembed_a3_20250307_145500/', device='cuda')
@app.route('/embed', methods=['POST'])
def embed():
    try:
        # Get text from JSON request
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        log_text: List[str] = data['text']
        if isinstance(log_text, str):
            log_text = [log_text]
            
        batch_size = min(128, len(log_text))
        total_batches = (len(log_text) + batch_size - 1) // batch_size
        
        all_embeddings = []

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(log_text))

            batch_sentences = log_text[start_idx:end_idx]
            batch_embeddings = model.encode(
                batch_sentences, 
                show_progress_bar=True
            )
            
            all_embeddings.append(batch_embeddings)
        
        if all_embeddings:
            embeddings_array = np.vstack(all_embeddings)
        else:
            print("Sumn wrong here")
            embeddings_array = np.array([]).reshape(0,0)
        
        return jsonify({
            'embeddings': embeddings_array.astype(float).tolist()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200)