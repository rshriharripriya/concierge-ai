"""
Hybrid retrieval combining BM25 keyword search + vector semantic search.
Uses Reciprocal Rank Fusion (RRF) to combine results.
"""
from typing import List, Dict, Optional
from supabase import Client
import os
from functools import lru_cache
import logging
import datetime

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
        self.base_recency_weight = float(os.getenv("RECENCY_WEIGHT", "0.4"))
        self.use_temporal = os.getenv("USE_TEMPORAL_RANKING", "true").lower() == "true"
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25"""
        # Lowercase and split on non-alphanumeric
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

    def _get_recency_weight(self, query: str, target_year: Optional[int]) -> float:
        """
        Adjust recency weight based on query specificity.
        """
        if target_year:
            current_year = datetime.datetime.now().year
            
            # If asking about a specific historical year (not current/last year)
            if target_year < current_year - 1:
                # Strong temporal enforcement for historical queries
                return 0.7  # 70% weight on matching exact year
            else:
                # Current or last year - moderate weight
                return 0.5
        else:
            # No specific year - default recency preference
            return self.base_recency_weight

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
            logger.warning(f"BM25 search failed: {e}. Using fallback vector search.")
            try:
                # Updated: Select metadata explicitly
                # Note: We fetch a small batch to treat as fallback. 
                # Ideally this should be a vector search, but using table fetch as requested.
                result = self.supabase.table('knowledge_documents')\
                    .select('id, title, content, source, category, metadata, created_at')\
                    .limit(k * 2)\
                    .execute()
                
                # Calculate similarity in Python (since we can't use the RPC)
                # Note: Real similarity calculation requires embeddings which we aren't fetching here.
                # Returning documents with neutral score as fallback.
                
                docs = []
                # Handle potential None result.data
                data = result.data if result.data else []
                
                for doc in data:
                    # Add mock scores for fallback
                    doc['bm25_score'] = 0.0
                    doc['similarity'] = 0.5  # Neutral score
                    docs.append(doc)
                
                return docs[:k]
            except Exception as e2:
                logger.error(f"Fallback fetch failed: {e2}")
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
    
    def _extract_target_year(self, query: str) -> Optional[int]:
        """
        Extract explicit year references from query with filing season awareness.
        """
        current_calendar_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        
        # Filing season awareness: Jan-Apr focuses on previous tax year
        if 1 <= current_month <= 4:
            current_tax_year = current_calendar_year - 1  # 2025 in Feb 2026
        else:
            current_tax_year = current_calendar_year
        
        # Pattern 1: "this year", "current year", "latest"
        current_patterns = [
            r'\bthis year\b', r'\bcurrent year\b', r'\bthis tax year\b',
            r'\bcurrent\b', r'\blatest\b'
        ]
        
        if any(re.search(p, query, re.IGNORECASE) for p in current_patterns):
            logger.debug(f"'This year' detected → {current_tax_year} (filing season aware)")
            return current_tax_year  # Returns 2025 in Feb 2026
        
        # Pattern 2: "last year", "previous year"
        if re.search(r'\blast year\b', query, re.IGNORECASE):
            last_year = current_tax_year - 1  # FIXED: 2025 - 1 = 2024
            logger.debug(f"'Last year' detected → {last_year}")
            return last_year
        
        if re.search(r'\bprevious year\b', query, re.IGNORECASE):
            prev_year = current_tax_year - 1  # FIXED: uses tax year
            logger.debug(f"'Previous year' detected → {prev_year}")
            return prev_year
        
        # Pattern 3: Explicit 4-digit years
        explicit_patterns = [
            r'\btax year (\d{4})\b',
            r'\bin (\d{4})\b',
            r'\bfor (\d{4})\b',
            r'\b(\d{4})\b',
        ]
        
        for pattern in explicit_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                if 2000 <= year <= current_calendar_year + 1:
                    logger.debug(f"Explicit year detected: {year}")
                    return year
        
        # No temporal keywords
        return None

    def _calculate_temporal_score(
        self, 
        doc_metadata: dict,
        target_year: Optional[int] = None
    ) -> float:
        """
        Calculate temporal relevance with support for multi-year documents.
        """
        current_year = datetime.datetime.now().year
        
        # Get all years mentioned in document
        tax_years = doc_metadata.get('tax_years', [])
        primary_year = doc_metadata.get('primary_tax_year')
        
        # Fallback if no tax_years extracted
        if not tax_years and not primary_year:
            return 0.05  # Neutral score
        
        # Convert to list if needed
        if not isinstance(tax_years, list):
            tax_years = [tax_years] if tax_years else []
        
        if not tax_years and primary_year:
            tax_years = [primary_year]
        
        # Convert string years to integers
        tax_years = [int(y) if isinstance(y, str) else y for y in tax_years if y]
        
        if not tax_years:
            return 0.5
        
        if target_year is None:
            # Default: Use most recent year in document
            most_recent = max(tax_years)
            year_diff = current_year - most_recent
            
            if year_diff == 0:
                temporal_score = 1.0  # Current year
            elif year_diff == 1:
                temporal_score = 0.6  # Last year
            elif year_diff == 2:
                temporal_score = 0.3  # 2 years old
            else:
                temporal_score = 0.1  # Older
            
            logger.debug(f"Multi-year doc {tax_years}, using most recent {most_recent} -> score {temporal_score:.3f}")
        else:
            # User asked about specific year
            if target_year in tax_years:
                temporal_score = 1.0
                logger.debug(f"Target year {target_year} found in {tax_years} -> score 1.0")
            else:
                # Check proximity to closest year
                closest_year = min(tax_years, key=lambda y: abs(y - target_year))
                year_diff = abs(closest_year - target_year)
                
                if year_diff == 1:
                    temporal_score = 0.3
                else:
                    temporal_score = 0.1
                
                logger.debug(f"Target year {target_year} not in {tax_years}, closest {closest_year} -> score {temporal_score:.3f}")
        
        return temporal_score

    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[Dict],
        vector_results: List[Dict],
        k: int = 60,
        query: str = None
    ) -> List[Dict]:
        """
        Enhanced RRF with optional temporal awareness.
        """
        scores = {}
        doc_map = {}
        
        # Standard RRF scoring
        for rank, doc in enumerate(bm25_results):
            doc_id = doc['id']
            scores[doc_id] = scores.get(doc_id, 0) + (1.0 / (k + rank + 1))
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
                doc_map[doc_id]['bm25_rank'] = rank + 1
                doc_map[doc_id]['bm25_score'] = doc.get('bm25_score', 0.0)
        
        for rank, doc in enumerate(vector_results):
            doc_id = doc['id']
            scores[doc_id] = scores.get(doc_id, 0) + (1.0 / (k + rank + 1))
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
            doc_map[doc_id]['vector_rank'] = rank + 1
            doc_map[doc_id]['similarity'] = doc.get('similarity', 0.0)
        
        # Apply temporal scoring if enabled and query provided
        if self.use_temporal and query:
            target_year = self._extract_target_year(query)
            recency_weight = self._get_recency_weight(query, target_year)
            
            # Log temporal settings
            logger.info(f"🕒 Target year: {target_year}, recency_weight: {recency_weight:.2f}")
            # Normalize RRF scores to 0-1
            max_rrf = max(scores.values()) if scores else 1.0
            normalized_rrf = {doc_id: score / max_rrf for doc_id, score in scores.items()}
            
            # Calculate final scores with temporal component
            final_scores = {}
            for doc_id, rrf_score in normalized_rrf.items():
                doc = doc_map[doc_id]
                doc_metadata = doc.get('metadata', {}) or {}
                
                temporal_score = self._calculate_temporal_score(doc_metadata, target_year)
                
                # Combine RRF and temporal
                final_scores[doc_id] = (
                    (1 - recency_weight) * rrf_score + 
                    recency_weight * temporal_score
                )
                
                # Store for debugging
                doc_map[doc_id]['temporal_score'] = temporal_score
                doc_map[doc_id]['rrf_score'] = rrf_score
                doc_map[doc_id]['final_score'] = final_scores[doc_id]
            
            sorted_ids = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        else:
            # No temporal scoring - use pure RRF
            sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for doc_id, rrf_score in sorted_ids:
                doc_map[doc_id]['rrf_score'] = rrf_score
                doc_map[doc_id]['hybrid_score'] = rrf_score
        
        # Build final results
        fused_results = []
        for doc_id, final_score in sorted_ids:
            doc = doc_map[doc_id]
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
        
        # Retrieve MORE initially for better temporal re-ranking
        # This ensures we capture docs from less-represented years (e.g., 2023)
        initial_k = k * 3
        
        try:
            # Run both searches in parallel (async)
            import asyncio
            # Pass dynamic weight to BM25 search
            bm25_results, vector_results = await asyncio.gather(
                self.retrieve_bm25(query, initial_k, weight=bm25_w),
                self.retrieve_vector(query, initial_k)
            )
            
            # Fuse results using RRF with temporal scoring
            fused_results = self._reciprocal_rank_fusion(
                bm25_results, 
                vector_results,
                query=query  # Pass query for temporal extraction
            )
            
            logger.info(f"Hybrid search fused {len(fused_results)} unique documents, returning top {k}")
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
