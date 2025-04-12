from sentence_transformers import SentenceTransformer, util
import re
import torch

class NLP:
    def __init__(self, model: str, threshold: float):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.transformer = SentenceTransformer(model, device=device)
        self.transformer = SentenceTransformer(model)  
        self.threshold = threshold

    def text_query(self, base_text: str, query_text: str):

        # Divide base_text in chunks by phrase
        chunks = re.split(r'(?<=[.!?])\s+', base_text)

        max_similarity = 0.0

        # embed query_text
        embedding_query = self.transformer.encode(query_text, convert_to_tensor=True)
        
        for chunk in chunks:
            if not chunk.strip():
                continue    #avoid empty chunks

            embedding_chunk = self.transformer.encode(chunk, convert_to_tensor=True)

            similarity = util.cos_sim(embedding_chunk, embedding_query).item()

            if similarity > self.threshold:
                return True

            if similarity > max_similarity:
                max_similarity = similarity

        return max_similarity>self.threshold
