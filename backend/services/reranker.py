"""
Reranking service with Cohere API backend.
Improves retrieval relevance by reranking top-k results.
"""
from typing import List, Dict, Optional
import os
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    logger.warning("Cohere not installed. Reranking will be skipped.")

@lru_cache(maxsize=1)
def get_cohere_client():
    """Cached Cohere client"""
    if not COHERE_AVAILABLE:
        return None
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        logger.warning("COHERE_API_KEY not set. Reranking disabled.")
        return None
    return cohere.Client(api_key)

class CohereReranker:
    """Reranker using Cohere Rerank API"""
    
    def __init__(self):
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            # Warn instead of crash to allow fallback
            logger.warning("COHERE_API_KEY not found in environment. Reranking will be disabled.")
            self.client = None
            self.enabled = False
            return
            
        self.client = cohere.Client(api_key)
        self.enabled = os.getenv("USE_RERANKING", "true").lower() == "true"
        if self.enabled:
            print("✅ Cohere reranker initialized")
    
    async def rerank(
        self, 
        query: str, 
        documents: List[Dict], 
        top_n: int = 5,
        model: str = "rerank-english-v3.0"
    ) -> List[Dict]:
        """
        Rerank documents using Cohere Rerank API.
        
        Args:
            query: User query
            documents: List of documents with 'content' field
            top_n: Number of top results to return
            model: Cohere rerank model name
            
        Returns:
            Reranked documents with 'rerank_score' field added
        """
        if not self.enabled or not self.client or not documents:
            logger.info("Reranking disabled or no documents, returning original order")
            return documents[:top_n]
        
        try:
            # Extract content for reranking
            doc_texts = [doc.get('content', '') for doc in documents]
            
            # Call Cohere Rerank API
            logger.info(f"Reranking {len(documents)} documents with Cohere {model}")
            
            # Using synchronous client in async method (Cohere SDK is sync)
            response = self.client.rerank(
                model=model,
                query=query,
                documents=doc_texts,
                top_n=top_n,
                return_documents=True  # Critical for faithfulness/context
            )
            
            logger.info(f"✅ Cohere reranked {len(documents)} → {len(response.results)} docs")
            
            # Reconstruct documents with new scores and order
            reranked_docs = []
            for result in response.results:
                # result.document.text contains the content
                # We need to map back to original metadata if possible, 
                # but since we passed text, we might lose metadata if we don't map by index.
                # result.index tells us the index in original list.
                
                original_doc = documents[result.index]
                
                reranked_doc = {
                    **original_doc,
                    'content': result.document.text, # Use the returned text to be safe
                    'rerank_score': result.relevance_score,
                    'rerank_index': result.index,
                    'similarity': original_doc.get('similarity', 0),
                    'combined_score': original_doc.get('combined_score', 0)
                }
                reranked_docs.append(reranked_doc)
            
            logger.info(f"✅ Cohere reranked {len(documents)} → {len(response.results)} docs")
            return reranked_docs
        
        except Exception as e:
            logger.error(f"❌ Reranking failed: {e}")
            # Fail gracefully - return original docs
            return documents[:top_n]

# Global instance
service_instance = None

def initialize():
    """Initialize the reranker service"""
    global service_instance
    try:
        service_instance = CohereReranker()
        if service_instance.enabled:
            logger.info("✅ Cohere reranker initialized and enabled")
        else:
            logger.info("⚠️ Cohere reranker initialized but disabled (check COHERE_API_KEY and USE_RERANKING)")
    except Exception as e:
        logger.error(f"⚠️ Reranker initialization failed: {e}")
        service_instance = None
