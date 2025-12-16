"""
Lightweight HuggingFace Embeddings wrapper using only the API.
Replaces langchain-huggingface which has heavy transformers dependencies.
"""
import os
import requests
from typing import List
from functools import lru_cache

class HuggingFaceEmbeddings:
    """Lightweight HuggingFace embedding client using Inference API"""
    
    def __init__(
        self,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_token: str = None
    ):
        self.model = model
        self.api_token = api_token or os.getenv("HF_TOKEN")
        # Use new router endpoint (api-inference.huggingface.co is completely deprecated)
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{model}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text"""
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": text}
        )
        response.raise_for_status()
        return response.json()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_query(text))
        return embeddings
