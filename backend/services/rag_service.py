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
        reranker.initialize()  # Initialize reranker!
        self.retriever = hybrid_retriever.service_instance
        self.reranker = reranker.service_instance

        # Model Config
        self.model = os.getenv("RAG_MODEL", "gemini-2.5-flash-lite-preview-09-2025")
        self.contextualize_system_prompt = (
            "Given the conversation history and a follow-up question, "
            "rewrite the follow-up as a standalone question with no pronouns or references."
        )

        self.contextualize_user_template = (
            "Conversation history:\n{conversationhistory}\n\n"
            "Follow-up question: {query}\n\n"
            "Standalone question:"
        )
        fallbacks_str = os.getenv("RAG_FALLBACKS", "")
        self.fallbacks = [f.strip() for f in fallbacks_str.split(",")] if fallbacks_str else [
            "groq/llama-3.3-70b-versatile",
            "openrouter/google/gemini-2.0-flash-exp:free"
        ]
        
        # Main RAG prompt for answer generation
        self.system_prompt_template = """You are a knowledgeable tax assistant providing accurate, focused answers.
CRITICAL TAX YEAR RULES:
1. Each source shows "📅 APPLICABLE TAX YEAR(S)" - this is THE DEFINITIVE tax year for that information
2. Sources may mention OTHER years as historical examples - IGNORE those
3. Only use amounts/rules from sources with tax years matching the user's query
4. If user asks "this year", they mean tax year {current_tax_year} (current filing season)
5. Sources marked "⭐ [CURRENT YEAR FOR FILING]" are for the current tax year

CRITICAL TAX FILING RULES:
- Standard deduction varies by FILING STATUS
- Single ≠ Married Filing Jointly - these are DIFFERENT amounts
- Always state which filing status you're referring to

CRITICAL: Retrieved sources are ranked by relevance (Source 1 = most relevant and most trustworthy).
Current date: {current_date}
Current tax year being filed: {current_tax_year}

ANSWER FORMAT:
1. **First sentence = Direct answer with specific numbers/facts**: "For 2025, the standard deduction is $15,000 for single filers [1]."
2. **Then add details as bullets when there are 2+ key points**:
   - One fact per bullet
   - Include citations [1], [2]
   - No filler words
3. **Length guide**:
   - Simple factual questions (amounts, deadlines): 1-2 sentences + bullets if needed
   - Procedural questions (how to do X): Short intro + bulleted steps
   - Complex scenarios: Comprehensive breakdown with sections

WHAT TO DO:
✅ Check the "📅 APPLICABLE TAX YEAR(S)" header for each source
✅ Lead with dollar amounts, dates, form numbers from Source 1
✅ Use bullets for lists, eligibility rules, multiple options
✅ Cite every factual statement with [1], [2]
✅ Prioritize information from highest-ranked sources

WHAT NOT TO DO:
❌ Don't start with definitions ("The standard deduction is a dollar amount that...")
❌ Don't write long paragraphs when bullets are clearer
❌ Don't ask follow-up questions for universal rules
❌ Don't say "not specified" if the info exists in sources

EXAMPLES:

Query: "What is the standard deduction for this year?"
✅ GOOD: "For tax year 2025, the standard deduction is $15,000 for single filers and $30,000 for married filing jointly [1]. Additional amounts:
- Age 65+: Add $1,850 if single, $1,500 if married [1]
- Blind: Same additional amounts apply [2]"

❌ BAD: "The standard deduction is a dollar amount that reduces your taxable income [1]. Most taxpayers can choose between taking the standard deduction or itemizing..."

Query: "Do I need to report interest from my savings account?"
✅ GOOD: "Yes, if you earned $10 or more in interest, you must report it [1]. Steps:
- You'll receive Form 1099-INT from your bank [1]
- Report on Schedule B of Form 1040 [2]"

❌ BAD: "Yes, you generally need to report interest... To give you more specific information, what is your filing status?"

Query: "Can I deduct my car?"
✅ GOOD: "You can deduct car expenses if you're self-employed or a business owner [1]. Two methods:
- **Standard Mileage**: $0.67/mile for 2024 [2]
- **Actual Expenses**: Gas, insurance, repairs (track business vs personal mileage) [3]

Note: W-2 employees cannot deduct commuting or personal vehicle expenses [2]."

❌ BAD: [Generic answer without clarifying who qualifies] + "Are you self-employed or an employee?"

Previous conversation:
{conversation_history}

Retrieved Context (ordered by relevance - prioritize Source 1):
{context}"""


    
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
            logger.error(f"Error fetching history: {e}")
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
            
            # Step 2: Rerank (ALWAYS for tax domain)
            # Log candidates BEFORE reranking
            logger.info(f"🔍 Hybrid search returned {len(candidates)} candidates")
            logger.info("Before reranking (Top 3):")
            for i, doc in enumerate(candidates[:3]):
                score = doc.get('combined_score') or doc.get('similarity') or 0
                title = doc.get('title', 'Unknown')
                logger.info(f"  #{i+1}: {title[:50]}... (score: {score:.3f})")
            query_lower = query.lower()
            # if 'standard deduction' in query_lower:
            #     # Filter out IRA/retirement docs, but preserve chunks with actual standard deduction content
            #     filtered_candidates = []
            #     for doc in candidates:
            #         title_lower = doc.get('title', '').lower()
            #         content_lower = doc.get('content', '').lower()
                    
            #         is_ira_title = any(kw in title_lower for kw in ['590-b', '590-a', 'ira contribution', 'retirement'])
            #         has_std_ded_content = 'table 10-1' in content_lower
                    
            #         if not is_ira_title or has_std_ded_content:
            #             filtered_candidates.append(doc)
            #         else:
            #             logger.debug(f"⏭️ Filtered IRA doc: {doc.get('title', '')[:60]}")
                
            #     candidates = filtered_candidates
            #     logger.info(f"🔪 Filtered IRA docs, {len(candidates)} candidates remaining")
            if self.reranker and self.reranker.enabled and len(candidates) > 0:
                logger.info(f"🎯 Reranking {len(candidates)} candidates to top-{k}")
                reranked = await self.reranker.rerank(query, candidates, top_n=k)
                
                # Log results AFTER reranking
                logger.info("After reranking (Top 3):")
                for i, doc in enumerate(reranked[:3]):
                    score = doc.get('rerank_score', 0)
                    title = doc.get('title', 'Unknown')
                    logger.info(f"  #{i+1}: {title[:50]}... (rerank: {score:.3f})")
            else:
                logger.warning("⚠️ Reranker not available/enabled! Using hybrid results directly")
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
                
                # Capture original scores BEFORE expansion to preserve them
                original_similarity = result.get('similarity', 0)
                original_rerank_score = result.get('rerank_score', 0)
                original_combined_score = result.get('combined_score', 0)
                
                # If no chapter info, use chunk as-is
                if not all([chapter, chunk_index, total_chunks]):
                    expanded_results.append(result)
                    continue
                
                # Fetch surrounding chunks from same chapter
                start_idx = max(1, chunk_index - expand_chunks)
                end_idx = min(total_chunks, chunk_index + expand_chunks)
                
                try:
                    context_chunks = self.supabase.table('knowledge_documents')\
                        .select('content, metadata') \
                        .eq('metadata->>chapter', chapter) \
                        .filter("(metadata->>'chunk_index')::int", "gte", start_idx) \
                        .filter("(metadata->>'chunk_index')::int", "lte", end_idx) \
                        .order("metadata->>'chunk_index'") \
                        .execute()
                    
                    if context_chunks.data:
                        logger.info(f"🔍 Expansion data sample: {context_chunks.data[0].keys()}")
                        logger.info(f"🔍 First chunk content length: {len(context_chunks.data[0].get('content', ''))}")
                        logger.info(f"🔍 First chunk metadata: {context_chunks.data[0].get('metadata', {})}")
                        # Merge into single context window
                        expanded_content = '\n\n'.join([
                            chunk['content'] for chunk in context_chunks.data
                        ])
                        
                        expanded_results.append({
                            **result,  # Keep original fields
                            'content': expanded_content,  # Replace with expanded content
                            'similarity': original_similarity,  # Explicitly restore
                            'rerank_score': original_rerank_score,  # Explicitly restore
                            'combined_score': original_combined_score,  # Explicitly restore
                            'metadata': {
                                **metadata,
                                'expanded': True,
                                'context_chunks': len(context_chunks.data),
                                'original_chunk_index': chunk_index  # Track which chunk matched
                            }
                        })
                        logger.info(f"Expanded chunk {chunk_index} with {len(context_chunks.data)} chunks, similarity: {original_similarity:.3f}, rerank: {original_rerank_score:.3f}")
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
            if not self.enabled:
                return query

            user_msg = self.contextualize_user_template.format(
                conversation_history=conversation_history,
                query=query
            )
            
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.contextualize_system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                fallbacks=self.fallbacks,
                temperature=0.1,
                timeout=10,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"⚠️ Query contextualization failed: {e}")
            return query

    async def generate_answer(self, query: str, conversation_id: str = None) -> Dict:
        """Generate RAG-based answer with conversation memory"""
        logger.info(f"🚨 GENERATE_ANSWER CALLED WITH QUERY: '{query}'")
        
        # Define datetime variables at the beginning to avoid scope issues
        import datetime
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        
        # Filing season logic: During Jan-Apr, "this year" means previous tax year
        if 1 <= current_month <= 4:
            tax_year = current_year - 1  # Feb 2026 → 2025
        else:
            tax_year = current_year
        
        # Get conversation history
        conversation_history = await self.get_conversation_history(conversation_id)
        
        # Contextualize query if history exists
        standalone_query = await self.contextualize_query(query, conversation_history)
        logger.info(f"🔄 Original query: '{query}' -> Standalone: '{standalone_query}'")
        

        # Retrieve relevant documents using STANDALONE query
        # Use RERANK_FINAL_K from env (default 8)
        final_k = int(os.getenv("RERANK_FINAL_K", "5"))
        documents = await self.retrieve_documents(standalone_query, k=final_k)
        # Debug: Log what was retrieved
        logger.info(f"📄 Retrieved {len(documents)} docs for query: '{standalone_query}'")
        for i, doc in enumerate(documents[:3], 1):
            tax_years = doc.get('metadata', {}).get('tax_years', 'N/A')
            title = doc.get('title', 'Unknown')[:60]
            logger.info(f"  Doc {i}: {title}... (years: {tax_years})")

        if not documents or len(documents) == 0:
            return {
                "answer": "I don't have enough information in my knowledge base to answer this question confidently. Let me connect you with an expert who can provide personalized guidance.",
                "sources": [],
                "confidence": 0.3
            }
        
        # Smart Context Construction (Total Budget)
        # Truncate the TOTAL context, not each document
        MAX_TOTAL_CONTEXT = int(os.getenv("MAX_TOTAL_CONTEXT", "8000"))  # Total char budget
        
        context_parts = []
        total_chars = 0

        for i, doc in enumerate(documents):
            # Extract metadata
            metadata = doc.get('metadata', {}) or {}
            tax_years = metadata.get('tax_years', [])
            is_current = metadata.get('is_current', False)
            primary_tax_year = metadata.get('primary_tax_year')
            
            # Build enhanced header with tax year info
            relevance = doc.get('rerank_score') or doc.get('similarity', 0)
            source_header = f"[Source {i+1} - Relevance: {relevance:.2f}]\n"
            
            # Add tax year badge (CRITICAL for LLM)
            if tax_years:
                years_str = ", ".join(str(y) for y in tax_years)
                source_header += f"📅 APPLICABLE TAX YEAR(S): {years_str}"
                if is_current:
                    source_header += " ⭐ [CURRENT YEAR FOR FILING]"
                source_header += "\n"
            
            source_header += f"Document: {doc['title']}\n"
            source_header += "IMPORTANT: Standard deduction amounts differ by filing status (Single ≠ Married Filing Jointly)\n\n"
            
            # Calculate remaining space
            available_space = MAX_TOTAL_CONTEXT - total_chars - len(source_header)
            
            if available_space < 200:  # Minimum useful chunk size
                break

            # Use available space for this doc
            content_to_use = doc['content'][:available_space]
            context_parts.append(f"{source_header}{content_to_use}")
            
            total_chars += len(source_header) + len(content_to_use)
            
            # Stop if we've filled the budget
            if total_chars >= MAX_TOTAL_CONTEXT:
                break
                
        context = "\n\n".join(context_parts)
        
        try:
            if not self.enabled:
                raise Exception("LiteLLM not available")
            
            # Clarify query with explicit tax year
            display_query = query.replace("this year", f"this year (tax year {tax_year})")
            display_query = display_query.replace("This year", f"This year (tax year {tax_year})")
            logger.info(f"📝 Clarified query for LLM: '{display_query}'")

            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt_template.format(
                        conversation_history=conversation_history,
                        context=context,
                        current_date=current_date, 
                        current_tax_year=tax_year
                    )},
                    {"role": "user", "content": display_query}  # Clarified query
                ],
                fallbacks=self.fallbacks,
                temperature=0.4,
                timeout=30,
                max_tokens=1000
            )


            
            # LiteLLM response structure differs from LangChain
            message_content = response.choices[0].message.content
            
            # # After: message_content = response.choices[0].message.content

            # # Check for vague answers to specific questions
            # vague_indicators = [
            #     "is a dollar amount that",
            #     "can be higher for",
            #     "generally limited",
            #     "reduces your taxable income"
            # ]

            # query_wants_amount = any(phrase in query.lower() for phrase in [
            #     "what is", "how much", "standard deduction", "tax bracket"
            # ])

            # answer_is_vague = any(indicator in message_content.lower() for indicator in vague_indicators)
            # has_specific_number = bool(re.search(r'\$[\d,]+', message_content))

            # if query_wants_amount and answer_is_vague and not has_specific_number:
            #     logger.warning(f"⚠️ Detected vague answer for factual query. Attempting clarification...")
            #     # Try again with more forceful prompt
            #     clarify_prompt = f"The user asked: '{query}'. They want SPECIFIC DOLLAR AMOUNTS from the sources, not a general definition. What are the exact standard deduction amounts for the tax year mentioned in the sources?"
                
            #     # Add clarification message
            #     message_content = f"{message_content}\n\n(Note: For specific dollar amounts, please ask about a particular tax year like '2025' or 'last year'.)"


            # Calculate immediate confidence (without faith faithfulness - async)
            # This doesn't block the user response
            max_similarity = max(
                doc.get('rerank_score') or doc.get('similarity', 0) 
                for doc in documents
            )
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
            
            # Deduplicate sources
            unique_sources = []
            source_map = {} # original_index -> new_index
            seen_titles = {} # title -> new_index
            
            for i, doc in enumerate(documents):
                title = doc['title']
                if title in seen_titles:
                    # Map to existing source
                    source_map[i + 1] = seen_titles[title] + 1
                    # Update score if this chunk has higher relevance
                    existing_doc = unique_sources[seen_titles[title]]
                    current_score = doc.get('rerank_score') or doc.get('similarity', 0)
                    existing_score = existing_doc.get('similarity', 0)
                    if current_score > existing_score:
                        existing_doc['similarity'] = current_score
                        existing_doc['rerank_score'] = doc.get('rerank_score')
                else:
                    # Add new source
                    new_index = len(unique_sources)
                    seen_titles[title] = new_index
                    source_map[i + 1] = new_index + 1
                    
                    unique_sources.append({
                        "title": title,
                        "source": doc.get('source', 'Internal'),
                        "similarity": doc.get('rerank_score') or doc.get('similarity', 0),
                        "rerank_score": doc.get('rerank_score'),
                        "original_similarity": doc.get('similarity'),
                        "chapter": doc.get('metadata', {}).get('chapter') if isinstance(doc.get('metadata'), dict) else None,
                        "source_url": doc.get('metadata', {}).get('source_url') if isinstance(doc.get('metadata'), dict) else None
                    })
            
            # Rewrite citations in answer
            # Map [3] -> [1] if 3 maps to 1
            def replace_citation(match):
                original_num = int(match.group(1))
                if original_num in source_map:
                    return f"[{source_map[original_num]}]"
                return match.group(0)
                
            filtered_answer = re.sub(r'\[(\d+)\]', replace_citation, cleaned_answer)

            return {
                "answer": filtered_answer,
                "sources": unique_sources,
                "contexts": [doc['content'] for doc in documents],
                "confidence": round(confidence, 2)
            }
        
        except Exception:
            # Clean logging
            logger.error("⚠️ RAG generation failed: All providers exhausted. Connecting to human support.")
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
        logger.info("🔥 Pre-warming RAG service...")
        _ = get_embeddings().embed_query("warmup query")
        logger.info("✅ RAG service ready")
    except Exception as e:
        logger.error(f"⚠️ RAGService initialization failed: {e}")
        service_instance = None

