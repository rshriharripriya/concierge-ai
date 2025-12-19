"""
Lightweight HuggingFace Embeddings wrapper using the official InferenceClient.
Replaces langchain-huggingface which has heavy transformers dependencies.
"""
import os
from typing import List
from functools import lru_cache
from huggingface_hub import InferenceClient

class HuggingFaceEmbeddings:
    """Lightweight HuggingFace embedding client using InferenceClient"""
    
    def __init__(
        self,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_token: str = None
    ):
        self.model = model
        self.api_token = api_token or os.getenv("HF_TOKEN")
        # Use official InferenceClient which handles endpoints and auth correctly
        self.client = InferenceClient(token=self.api_token)
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text"""
        # Use feature_extraction endpoint
        result = self.client.feature_extraction(text, model=self.model)
        # Result is already a list of floats
        return result.tolist() if hasattr(result, 'tolist') else result
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_query(text))
        return embeddings
