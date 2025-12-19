"""
Hybrid retrieval combining BM25 keyword search + vector semantic search.
Uses Reciprocal Rank Fusion (RRF) to combine results.
"""
from typing import List, Dict, Optional
from supabase import Client
import os
from functools import lru_cache
import logging
from rank_bm25 import BM25Okapi
import re

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_supabase():
    """Cached Supabase client"""
    from supabase import create_client
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

class HybridRetriever:
    """Hybrid search combining BM25 + vector similarity"""
    
    def __init__(self, embeddings):
        self.supabase: Client = get_supabase()
        self.embeddings = embeddings
        self.bm25_weight = float(os.getenv("BM25_WEIGHT", "0.6"))
        self.vector_weight = float(os.getenv("VECTOR_WEIGHT", "0.4"))
        self.use_hybrid = os.getenv("USE_HYBRID_SEARCH", "true").lower() == "true"
        self.use_dynamic_weights = os.getenv("USE_DYNAMIC_WEIGHTS", "true").lower() == "true"
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25"""
        # Lowercase and split on non-alphanumeric
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
        
    def _get_dynamic_weights(self, query: str) -> Dict[str, float]:
        """
        Detect query type and adjust BM25 vs Vector weights
        Returns:
            dict with 'bm25' and 'vector' weights
        """
        if not self.use_dynamic_weights:
            return {"bm25": self.bm25_weight, "vector": self.vector_weight}
            
        # 1. Define patterns that need EXACT matching
        exact_patterns = [
            r'\bForm\s+\d+',           # "Form 1040", "Form 8889"
            r'\b\d{4}\b',              # Years: "2024", "2023"
            r'\bSchedule\s+[A-Z]\b',   # "Schedule C", "Schedule A"
            r'\bW-?\d+\b',             # "W-2", "W4"
            r'\b1099-\w+\b',           # "1099-INT", "1099-MISC"
            r'\bIRS\s+Publication\s+\d+',  # "IRS Publication 970"
        ]
        
        # 2. Check if query contains any exact patterns
        has_exact_terms = any(
            re.search(pattern, query, re.IGNORECASE) 
            for pattern in exact_patterns
        )
        
        # 3. Return appropriate weights
        if has_exact_terms:
            logger.info(f"🔍 Dynamic Weights: Detected exact terms in '{query}' -> Boosting BM25")
            return {"bm25": 0.7, "vector": 0.3}
        else:
            # Default balanced approach for conceptual queries
            # Use env defaults (usually 0.6/0.4)
            return {"bm25": self.bm25_weight, "vector": self.vector_weight}
    
    async def retrieve_bm25(self, query: str, k: int = 20, weight: float = None) -> List[Dict]:
        """
        Retrieve using PostgreSQL full-text search (BM25-like).
        """
        # Use provided weight or default
        bm25_weight = weight if weight is not None else self.bm25_weight
        # Use complement for vector if not provided (just for the rpc call signature compatibility)
        vector_weight = 1.0 - bm25_weight
        
        try:
            # Generate query embedding for hybrid search
            query_embedding = self.embeddings.embed_query(query)
            
            # Use PostgreSQL hybrid search function (BM25 + vector)
            result = self.supabase.rpc(
                'hybrid_search_knowledge_documents',
                {
                    'query_text': query,
                    'query_embedding': query_embedding,
                    'match_count': k,
                    'bm25_weight': bm25_weight,
                    'vector_weight': vector_weight
                }
            ).execute()
            
            if result.data:
                logger.info(f"BM25 retrieved {len(result.data)} documents")
                return result.data
            return []
            
        except Exception as e:
            # Fallback: if custom function doesn't exist, use basic vector search
            logger.warning(f"BM25 search failed: {e}. Using fallback vector search.")
            try:
                # Just do vector search as fallback
                query_embedding = self.embeddings.embed_query(query)
                result = self.supabase.rpc(
                    'match_knowledge_documents',
                    {
                        'query_embedding': query_embedding,
                        'match_count': k,
                        'match_threshold': 0.3
                    }
                ).execute()
                
                # Add mock BM25 score
                docs = result.data[:k] if result.data else []
                for doc in docs:
                    doc['bm25_score'] = 0.0  # No BM25 in fallback
                
                return docs
            except Exception as e2:
                logger.error(f"Fallback vector search also failed: {e2}")
                return []
    
    async def retrieve_vector(self, query: str, k: int = 20) -> List[Dict]:
        """
        Retrieve using vector similarity search.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of documents with similarity score
        """
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Vector search using pgvector
            result = self.supabase.rpc(
                'match_knowledge_documents',
                {
                    'query_embedding': query_embedding,
                    'match_count': k,
                    'match_threshold': 0.3
                }
            ).execute()
            
            if result.data:
                logger.info(f"Vector search retrieved {len(result.data)} documents")
                return result.data
            return []
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def _reciprocal_rank_fusion(
        self, 
        bm25_results: List[Dict], 
        vector_results: List[Dict],
        k: int = 60
    ) -> List[Dict]:
        """
        Combine results using Reciprocal Rank Fusion (RRF).
        
        RRF formula: score(doc) = sum(1 / (k + rank_i))
        Industry standard for hybrid search fusion.
        
        Args:
            bm25_results: Results from BM25 search
            vector_results: Results from vector search
            k: RRF constant (default 60)
            
        Returns:
            Fused and ranked results
        """
        scores = {}
        doc_map = {}
        
        # Add BM25 scores
        for rank, doc in enumerate(bm25_results):
            doc_id = doc['id']
            scores[doc_id] = scores.get(doc_id, 0) + (1.0 / (k + rank + 1))
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
                doc_map[doc_id]['bm25_rank'] = rank + 1
                doc_map[doc_id]['bm25_score'] = doc.get('bm25_score', 0.0)
        
        # Add vector scores
        for rank, doc in enumerate(vector_results):
            doc_id = doc['id']
            scores[doc_id] = scores.get(doc_id, 0) + (1.0 / (k + rank + 1))
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
            doc_map[doc_id]['vector_rank'] = rank + 1
            doc_map[doc_id]['similarity'] = doc.get('similarity', 0.0)
        
        # Sort by RRF score
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build final results with RRF score
        fused_results = []
        for doc_id, rrf_score in sorted_ids:
            doc = doc_map[doc_id]
            doc['rrf_score'] = rrf_score
            doc['hybrid_score'] = rrf_score  # Alias for consistency
            fused_results.append(doc)
        
        return fused_results
    
    async def retrieve(self, query: str, k: int = 20) -> List[Dict]:
        """
        Hybrid retrieval combining BM25 + vector search.
        """
        if not self.use_hybrid:
            logger.info("Hybrid search disabled, using vector-only")
            return await self.retrieve_vector(query, k)
        
        # Calculate dynamic weights
        weights = self._get_dynamic_weights(query)
        bm25_w = weights["bm25"]
        
        try:
            # Run both searches in parallel (async)
            import asyncio
            # Pass dynamic weight to BM25 search
            bm25_results, vector_results = await asyncio.gather(
                self.retrieve_bm25(query, k, weight=bm25_w),
                self.retrieve_vector(query, k)
            )
            
            # Fuse results using RRF
            fused_results = self._reciprocal_rank_fusion(bm25_results, vector_results)
            
            logger.info(f"Hybrid search fused {len(fused_results)} unique documents")
            return fused_results[:k]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}. Falling back to vector-only.")
            return await self.retrieve_vector(query, k)

# Global instance will be created when RAG service initializes
service_instance = None

def initialize(embeddings):
    """Initialize hybrid retriever with embeddings"""
    global service_instance
    try:
        service_instance = HybridRetriever(embeddings)
        logger.info(f"✅ Hybrid retriever initialized (BM25: {service_instance.bm25_weight}, Vector: {service_instance.vector_weight})")
    except Exception as e:
        logger.error(f"⚠️ Hybrid retriever initialization failed: {e}")
        service_instance = None
