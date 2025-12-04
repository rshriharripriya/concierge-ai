from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def get_embeddings():
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

@lru_cache(maxsize=1)
def get_supabase():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

class ExpertMatcher:
    def __init__(self):
        self.supabase: Client = get_supabase()
        self.embeddings = get_embeddings()
    
    async def find_best_expert(self, query: str, intent: str, urgency: bool = False) -> Optional[Dict]:
        """
        Match query to best available expert using multi-factor scoring
        """
        
        try:
            # Get all experts
            experts_result = self.supabase.table('experts').select('*').execute()
            experts = experts_result.data
            
            if not experts or len(experts) == 0:
                return None
            
            # Score each expert
            scored_experts = []
            
            for expert in experts:
                # 1. Specialty match score (40% weight)
                specialties = expert.get('specialties', [])
                specialty_score = 0.0
                
                intent_domain = intent.split('_')[-1] if '_' in intent else intent
                
                if intent_domain in specialties:
                    specialty_score = 1.0
                elif any(intent_domain in spec or spec in intent for spec in specialties):
                    specialty_score = 0.7
                elif intent == 'bookkeeping' and any(s in specialties for s in ['bookkeeping', 'quickbooks']):
                    specialty_score = 1.0
                elif intent in ['complex_tax', 'simple_tax'] and 'tax' in specialties:
                    specialty_score = 0.9
                else:
                    specialty_score = 0.3
                
                # 2. Availability score (30% weight)
                availability = expert.get('availability', {})
                is_available = availability.get('status') == 'available'
                availability_score = 1.0 if is_available else 0.3
                
                # 3. Performance score (20% weight)
                metrics = expert.get('performance_metrics', {})
                avg_rating = metrics.get('avg_rating', 3.5)
                performance_score = avg_rating / 5.0
                
                if expert.get('expertise_embedding'):
                    # Calculate cosine similarity
                    query_embedding = self.embeddings.encode(query)
                    expert_embedding = expert['expertise_embedding']
                    
                    # Handle string representation of embedding
                    if isinstance(expert_embedding, str):
                        import json
                        try:
                            expert_embedding = json.loads(expert_embedding)
                        except:
                            # Handle Postgres array format '{0.1,0.2}' if JSON fails
                            expert_embedding = [float(x) for x in expert_embedding.strip('{}').split(',')]

                    # Manual cosine similarity calculation since embeddings are lists/arrays
                    import numpy as np
                    q_vec = np.array(query_embedding)
                    e_vec = np.array(expert_embedding)
                    
                    norm_q = np.linalg.norm(q_vec)
                    norm_e = np.linalg.norm(e_vec)
                    
                    if norm_q > 0 and norm_e > 0:
                        semantic_score = float(np.dot(q_vec, e_vec) / (norm_q * norm_e))
                
                # Calculate weighted final score
                final_score = (
                    specialty_score * 0.40 +
                    availability_score * 0.30 +
                    performance_score * 0.20 +
                    semantic_score * 0.10
                )
                
                if urgency and is_available:
                    final_score *= 1.2
                
                scored_experts.append({
                    **expert,
                    'match_score': round(final_score, 3)
                })
            
            # Sort by score descending
            scored_experts.sort(key=lambda x: x['match_score'], reverse=True)
            best_expert = scored_experts[0]
            
            is_available = best_expert['availability']['status'] == 'available'
            estimated_wait = "< 5 min" if is_available else "15-30 min"
            
            return {
                "expert_id": best_expert['id'],
                "expert_name": best_expert['name'],
                "expert_bio": best_expert['bio'],
                "avatar_url": best_expert['avatar_url'],
                "specialties": best_expert['specialties'],
                "match_score": best_expert['match_score'],
                "estimated_wait": estimated_wait,
                "performance": best_expert['performance_metrics']
            }
        
        except Exception as e:
            print(f"⚠️ Expert matching error: {e}")
            return None

# Singleton instance
expert_matcher = ExpertMatcher()
