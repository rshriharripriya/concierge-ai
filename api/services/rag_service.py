try:
    from litellm import completion
    import litellm
    import logging
    # Aggressively silence LiteLLM
    litellm.set_verbose = False
    litellm.suppress_handler_errors = True
    litellm.add_status_to_exception = False
    litellm.telemetry = False
    logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

from langchain_core.prompts import ChatPromptTemplate
from supabase import create_client, Client
from typing import List, Dict
import os
from functools import lru_cache
from services.hf_embeddings import HuggingFaceEmbeddings
import logging
import re

logger = logging.getLogger(__name__)

# Removed get_llm cached function as we now use LiteLLM completion directly in generate_answer

@lru_cache(maxsize=1)
def get_embeddings():
    """Cached HuggingFace Inference API Embeddings"""
    logger.info("🔄 Loading embedding model (API)...")
    model = HuggingFaceEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        api_token=os.getenv("HF_TOKEN")
    )
    logger.info("✅ Embedding model loaded")
    return model

@lru_cache(maxsize=1)
def get_supabase():
    """Cached Supabase client"""
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

class RAGService:
    def __init__(self):
        self.enabled = LITELLM_AVAILABLE
        self.embeddings = get_embeddings()
        self.supabase: Client = get_supabase()
        
        # Initialize hybrid retriever and reranker
        from services import hybrid_retriever, reranker
        hybrid_retriever.initialize(self.embeddings)
        self.retriever = hybrid_retriever.service_instance
        self.reranker = reranker.service_instance

        # Model Config
        self.model = os.getenv("RAG_MODEL", "gemini-2.5-flash-lite-preview-09-2025")
        fallbacks_str = os.getenv("RAG_FALLBACKS", "")
        self.fallbacks = [f.strip() for f in fallbacks_str.split(",")] if fallbacks_str else [
            "groq/llama-3.3-70b-versatile",
            "openrouter/google/gemini-2.0-flash-exp:free"
        ]
        
        # Main RAG prompt for answer generation
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a knowledgeable tax assistant. Answer questions using the provided context.

CRITICAL FORMATTING RULES (MUST FOLLOW):

1. MARKDOWN FORMATTING:
   - Use **bold** for key terms and important points
   - For bullet lists, use DASH (-) with proper line breaks:
   
- First item
- Second item
- Third item

   - NOT asterisks (*), NOT inline like "* item1 * item2"
   - Leave blank lines before and after lists

4. TEMPORAL RELEVANCE (CRITICAL):
   - PRIORITIZE 2024 information over 2023 or earlier.
   - If context contains conflicting numbers (e.g. 2023 vs 2024), USE THE 2024 NUMBERS.
   - Explicitly state "For 2024..." to confirm you are using the latest data.

2. CITATIONS (STRICT):
   - IF information comes from the provided context (numbers, specific rules), YOU MUST cite it using [1], [2], etc.
   - IF information is general knowledge (definitions, concepts), DO NOT cite it.
   - NEVER use "[No Citation]" or similar tags. Just leave it blank.
   - NEVER write "References:" section
   - Just use [1] at the end of sentences
   
3. COMPREHENSIVE ANSWERS - MINIMAL CLARIFICATION QUESTIONS:
   - For common tax questions (standard deduction, filing status, deadlines, etc), provide ALL relevant scenarios in your first response.
   - Example 1: \"What is the standard deduction?\"
     - Right now: \"What is your filing status?\" (❌ WRONG)
     - Improvement: \"Explain what standard deduction is and how it depends on your filing status and other factors:
       - If you are single: $X
       - If you are married filing jointly: $Y
       - If you are head of household: $Z
       If you can tell me your status, I could provide more detailed info.\" (✅ CORRECT)
   - Example 2: "Can I deduct my car?"
     - Improvement: Provide general rules for self-employed vs employees, and mention that if they provide more context (e.g., business use %), you can be more specific.
   
4. WHAT NOT TO DO:
   ❌ * inline * asterisks * for lists
   ❌ References: [1] Book - Author
   ❌ "Are you single or married?"
   ❌ "What is your filing status?"
   ❌ "Please tell me your income level first."
   
   ✅ Proper bullet lists with dashes
   ✅ Simple [1] citations only
   ✅ Comprehensive coverage: "For single filers: $X, for married: $Y"
   ✅ Proactive information gathering: "Based on common scenarios... [info]. If you provide [specific detail], I can refine this."

4. CONVERSATIONAL CLOSING:
   - For general questions where you provided multiple scenarios (e.g. single vs married),
     YOU MUST END WITH A QUESTION asking for their specific situation.
   - Example closing: "To give you an exact number, are you filing single, married, or head of household?"

Previous conversation:
{conversation_history}

Context:
{context}"""),
            ("user", "{query}")
        ])
        
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", """Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""),
            ("user", """Chat History:
{conversation_history}

User Question: {query}

Standalone Question:""")
        ])
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 3) -> str:
        """Retrieve recent conversation history (limited to save tokens)"""
        if not conversation_id:
            return "No prior conversation"
        
        try:
            result = self.supabase.table('messages')\
                .select('role, content')\
                .eq('conversation_id', conversation_id)\
                .order('created_at', desc=False)\
                .limit(limit)\
                .execute()
            
            if not result.data:
                return "No prior conversation"
            
            history_lines = []
            for msg in result.data[:-1]:  # Exclude current message
                role = "User" if msg['role'] == 'user' else "Assistant"
                history_lines.append(f"{role}: {msg['content']}")
            
            return "\n".join(history_lines) if history_lines else "No prior conversation"
        
        except Exception as e:
            print(f"Error fetching history: {e}")
            return "No prior conversation"
    
    async def retrieve_documents(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve relevant documents using hybrid search + reranking + contextual expansion.
        
        Implements "Search Small, Feed Big" strategy:
        - Search with small chunks (precise matching)
        - Expand by fetching neighboring chunks from same chapter
        - Feed large context to LLM (semantic coherence)
        """
        try:
            # Step 1: Hybrid retrieval (BM25 + Vector)
            # Get more documents than needed for reranking
            rerank_top_k = int(os.getenv("RERANK_TOP_K", "30"))
            
            if self.retriever:
                logger.info(f"Using hybrid retrieval (BM25 + vector) for top-{rerank_top_k}")
                candidates = await self.retriever.retrieve(query, k=rerank_top_k)
            else:
                # Fallback: vector-only search
                logger.warning("Hybrid retriever not available, using vector-only")
                query_embedding = self.embeddings.embed_query(query)
                result = self.supabase.rpc(
                    'match_knowledge_documents',
                    {
                        'query_embedding': query_embedding,
                        'match_count': rerank_top_k,
                        'match_threshold': 0.3
                    }
                ).execute()
                candidates = result.data if result.data else []
            
            # Step 2: Rerank if enabled and beneficial
            top_similarity = candidates[0].get('similarity', 0) if candidates else 0
            
            if self.reranker and self.reranker.enabled and len(candidates) > 0:
                if top_similarity > 0.95: # Increased threshold for skipping
                    logger.info(f"Skipping reranking (top similarity {top_similarity:.3f} > 0.95)")
                    reranked = candidates[:k]
                else:
                    logger.info(f"Reranking {len(candidates)} candidates to top-{k}")
                    reranked = await self.reranker.rerank(query, candidates, top_n=k)
            else:
                reranked = candidates[:k]
            
            # Step 3: CONTEXTUAL CHUNK EXPANSION
            # Fetch neighboring chunks from same chapter for better context
            expanded_results = []
            expand_chunks = int(os.getenv("CHUNK_EXPANSION_WINDOW", "1"))
            
            for result in reranked:
                metadata = result.get('metadata', {})
                chapter = metadata.get('chapter')
                chunk_index = metadata.get('chunk_index')
                total_chunks = metadata.get('total_chunks')
                
                # If no chapter info, use chunk as-is
                if not all([chapter, chunk_index, total_chunks]):
                    expanded_results.append(result)
                    continue
                
                # Fetch surrounding chunks from same chapter
                start_idx = max(1, chunk_index - expand_chunks)
                end_idx = min(total_chunks, chunk_index + expand_chunks)
                
                try:
                    context_chunks = self.supabase.table('knowledge_documents')\
                        .select('content, metadata')\
                        .eq('metadata->>chapter', chapter)\
                        .gte('metadata->>chunk_index', start_idx)\
                        .lte('metadata->>chunk_index', end_idx)\
                        .order('metadata->>chunk_index')\
                        .execute()
                    
                    if context_chunks.data:
                        # Merge into single context window
                        expanded_content = '\n\n'.join([
                            chunk['content'] for chunk in context_chunks.data
                        ])
                        
                        expanded_results.append({
                            **result,  # Keep original scores (similarity, rerank_score, etc.)
                            'content': expanded_content,  # Replace with expanded content
                            'metadata': {
                                **metadata,
                                'expanded': True,
                                'context_chunks': len(context_chunks.data),
                                'original_chunk_index': chunk_index  # Track which chunk matched
                            }
                        })
                        logger.info(f"Expanded chunk {chunk_index} with {len(context_chunks.data)} chunks, similarity: {result.get('similarity', 0):.3f}")
                    else:
                        expanded_results.append(result)
                except Exception as expand_error:
                    logger.warning(f"Context expansion failed: {expand_error}, using original chunk")
                    expanded_results.append(result)
            
            return expanded_results
        
        except Exception as e:
            logger.error(f"⚠️ Document retrieval error: {e}")
            return []
    
    async def contextualize_query(self, query: str, conversation_history: str) -> str:
        """Rewrite query to be standalone based on history"""
        if conversation_history == "No prior conversation":
            return query
            
        try:
            chain = self.contextualize_q_prompt | self.llm
            response = chain.invoke({
                "conversation_history": conversation_history,
                "query": query
            })
            return response.content
        except Exception as e:
            print(f"⚠️ Query contextualization failed: {e}")
            return query

    async def generate_answer(self, query: str, conversation_id: str = None) -> Dict:
        """Generate RAG-based answer with conversation memory"""
        
        # Get conversation history
        conversation_history = await self.get_conversation_history(conversation_id)
        
        # Contextualize query if history exists
        standalone_query = await self.contextualize_query(query, conversation_history)
        print(f"🔄 Original query: '{query}' -> Standalone: '{standalone_query}'")
        
        # Retrieve relevant documents using STANDALONE query
        # Use RERANK_FINAL_K from env (default 8)
        final_k = int(os.getenv("RERANK_FINAL_K", "8"))
        documents = await self.retrieve_documents(standalone_query, k=final_k)
        
        if not documents or len(documents) == 0:
            return {
                "answer": "I don't have enough information in my knowledge base to answer this question confidently. Let me connect you with an expert who can provide personalized guidance.",
                "sources": [],
                "confidence": 0.3
            }
        
        # Format context from retrieved documents (truncate to save tokens)
        MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "4000"))
        context = "\n\n".join([
            f"[Source {i+1}: {doc['title']}]\n{doc['content'][:MAX_CONTENT_LENGTH]}{'...' if len(doc['content']) > MAX_CONTENT_LENGTH else ''}\n(Relevance: {doc.get('similarity', 0):.2f})"
            for i, doc in enumerate(documents)
        ])
        
        try:
            if not self.enabled:
                raise Exception("LiteLLM not available")

            # Provider Chain: Configurable via env
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt.messages[0].prompt.template.format(
                        conversation_history=conversation_history,
                        context=context
                    )},
                    {"role": "user", "content": query}
                ],
                fallbacks=self.fallbacks,
                temperature=0.4, # Lower for tax accuracy
                timeout=30,
                max_tokens=1000
            )
            
            # LiteLLM response structure differs from LangChain
            message_content = response.choices[0].message.content
            
            # Calculate immediate confidence (without faith faithfulness - async)
            # This doesn't block the user response
            max_similarity = max(doc.get('similarity', 0) for doc in documents)
            rerank_score = max(doc.get('rerank_score', 0) for doc in documents) if documents else 0
            
            # Check for citations
            has_citations = bool(re.search(r'\[\d+\]', message_content))
            
            # Immediate confidence calculation
            from services.faithfulness_scorer import calculate_confidence
            retrieval_scores = {
                'max_similarity': max_similarity,
                'rerank_score': rerank_score
            }
            answer_metadata = {
                'has_citations': has_citations,
                'llm_confidence': 0.7  # Could extract from LLM if supported
            }
            
            confidence = calculate_confidence(
                retrieval_scores,
                answer_metadata,
                faithfulness_score=None  # Will be calculated async
            )
            
            # Aggressively clean citations
            cleaned_answer = message_content
            
            # Remove entire "References:" section at the end
            cleaned_answer = re.sub(r'\n\s*References?:.*$', '', cleaned_answer, flags=re.DOTALL | re.IGNORECASE)
            
            # Convert verbose citations to simple numbers
            # [Source 2: Title] -> [2]
            cleaned_answer = re.sub(r'\[Source\s+(\d+):\s+[^\]]+\]', r'[\1]', cleaned_answer)
            # [2: Title] -> [2]
            cleaned_answer = re.sub(r'\[(\d+):\s+[^\]]+\]', r'[\1]', cleaned_answer)
            # [2] Title - Author -> [2]
            cleaned_answer = re.sub(r'\[(\d+)\]\s+[^[\n]+?(?=\n|$)', r'[\1]', cleaned_answer)
            
            # Clean up whitespace
            cleaned_answer = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_answer)  # Max 2 newlines
            cleaned_answer = cleaned_answer.strip()
            
            return {
                "answer": cleaned_answer,
                "sources": [
                    {
                        "title": doc['title'],
                        "source": doc.get('source', 'Internal'),
                        "similarity": min(1.0, max(0.0, doc.get('similarity', 0) / 100 if doc.get('similarity', 0) > 1 else doc.get('similarity', 0))),  # Normalize to 0-1
                        "chapter": doc.get('metadata', {}).get('chapter') if isinstance(doc.get('metadata'), dict) else None,
                        "source_url": doc.get('metadata', {}).get('source_url') if isinstance(doc.get('metadata'), dict) else None
                    }
                    for doc in documents
                ],
                "contexts": [doc['content'] for doc in documents],
                "confidence": round(confidence, 2)
            }
        
        except Exception:
            # Clean logging
            print("⚠️ RAG generation failed: All providers exhausted. Connecting to human support.")
            return {
                "answer": "I'm having trouble providing a complete answer right now. Let me connect you with an expert who can help.",
                "sources": [],
                "contexts": [],
                "confidence": 0.2
            }

# Global instance
service_instance = None

def initialize():
    """Initialize the RAG service"""
    global service_instance
    try:
        service_instance = RAGService()
        # Pre-warm
        print("🔥 Pre-warming RAG service...")
        _ = get_embeddings().embed_query("warmup query")
        print("✅ RAG service ready")
    except Exception as e:
        print(f"⚠️ RAGService initialization failed: {e}")
        service_instance = None

