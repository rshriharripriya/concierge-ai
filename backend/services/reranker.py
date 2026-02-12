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
            logger.warning("COHERE_API_KEY not found. Reranking disabled.")
            self.client = None
            self.enabled = False
            self.model = None
            return
        
        self.client = cohere.Client(api_key)
        self.model = "rerank-english-v3.0"  # Cohere's best model
        self.enabled = os.getenv("USE_RERANKING", "true").lower() == "true"
    
        if self.enabled:
            logger.info("✅ Cohere reranker initialized")

    
    async def rerank(self, query: str, documents: List[Dict], top_n: int = 5) -> List[Dict]:
        """
        Rerank documents using Cohere with enriched context.
        """
        if not self.enabled or not documents:
            return documents[:top_n]
        
        try:
            logger.info(f"Reranking {len(documents)} documents with Cohere {self.model}")
            
            # STEP 1: Enrich documents with title + metadata
            enriched_docs = []
            for doc in documents:
                title = doc.get('title', '')
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                tax_years = metadata.get('tax_years', [])
                year_context = f" (Tax years: {', '.join(map(str, tax_years))})" if tax_years else ""
                
                enriched_text = f"Title: {title}{year_context}\n\n{content}"
                enriched_docs.append(enriched_text)
            
            # STEP 2: Call Cohere
            response = self.client.rerank(
                model=self.model,
                query=query,
                documents=enriched_docs,
                top_n=top_n,
                return_documents=False
            )
            
            # STEP 3: Map results back to original docs
            reranked = []
            for result in response.results:
                original_doc = documents[result.index]
                reranked.append({
                    **original_doc,
                    'rerank_score': result.relevance_score,
                    'rerank_index': result.index
                })
            
            logger.info(f"✅ Cohere reranked {len(documents)} → {len(reranked)} docs")
            
            # ============================================================
            # STEP 4: ADD TITLE BOOST HERE (After Cohere, before return)
            # ============================================================
            import re
            
            # Extract meaningful keywords from query
            query_keywords = set(re.findall(r'\b\w+\b', query.lower()))
    
            query_keywords -= {'the', 'is', 'a', 'for', 'what', 'how', 'this', 'year', 'my', 'can', 'i'}
            
            for doc in reranked:
                title = doc.get('title', '').lower()
                title_words = set(re.findall(r'\b\w+\b', title))
                
                # Count keyword matches in title
                matches = len(query_keywords & title_words)
                
                if matches >= 2:  # At least 2 keywords match
                    original_score = doc.get('rerank_score', 0)
                    boosted_score = min(1.0, original_score * 1.15)  # 15% boost, cap at 1.0
                    doc['rerank_score'] = boosted_score
                    logger.info(f"   📈 Title boost: '{title[:50]}' ({matches} keywords, {original_score:.3f} → {boosted_score:.3f})")
            
            # Re-sort by boosted scores
            reranked.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
            # ============================================================
            
            # Log final top 3 for debugging
            for i, doc in enumerate(reranked[:3], 1):
                title = doc.get('title', 'Unknown')[:60]
                score = doc.get('rerank_score', 0)
                logger.info(f"   Final #{i}: {title}... (score: {score:.3f})")
            
            return reranked[:top_n]  # Return after boosting and re-sorting
        
        except Exception as e:
            logger.error(f"❌ Cohere reranking failed: {e}")
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
