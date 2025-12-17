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
        self.client = get_cohere_client()
        self.enabled = self.client is not None and os.getenv("USE_RERANKING", "true").lower() == "true"
    
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
        if not self.enabled or not documents:
            logger.info("Reranking disabled or no documents, returning original order")
            return documents[:top_n]
        
        try:
            # Extract content for reranking
            doc_texts = [doc.get('content', '') for doc in documents]
            
            # Call Cohere Rerank API
            logger.info(f"Reranking {len(documents)} documents with Cohere {model}")
            results = self.client.rerank(
                model=model,
                query=query,
                documents=doc_texts,
                top_n=top_n,
                return_documents=False  # We already have the docs
            )
            
            # Merge rerank scores with original documents
            reranked_docs = []
            for result in results.results:
                original_doc = documents[result.index]
                reranked_doc = {
                    **original_doc,
                    'rerank_score': result.relevance_score,
                    'rerank_index': result.index
                }
                reranked_docs.append(reranked_doc)
            
            logger.info(f"Successfully reranked to top {len(reranked_docs)} documents")
            return reranked_docs
        
        except Exception as e:
            # Defensive: Handle Cohere rate limits (free tier: 10-20 req/min)
            if "429" in str(e) or "rate" in str(e).lower():
                logger.warning(f"⚠️ Cohere rate limit hit: {e}. Failing open with original ranking.")
            elif "trial" in str(e).lower() or "quota" in str(e).lower():
                logger.warning(f"⚠️ Cohere trial quota exceeded: {e}. Failing open.")
            else:
                logger.error(f"⚠️ Reranking failed: {e}. Failing open with original ranking.")
            
            # Fail open: return top-n from original ranking
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
