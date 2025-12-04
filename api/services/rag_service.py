from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from supabase import create_client, Client
from typing import List, Dict
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def get_llm():
    """Cached LLM instance"""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        timeout=25,
        max_retries=2
    )

@lru_cache(maxsize=1)
def get_embeddings():
    """Cached HuggingFace Inference API Embeddings"""
    print("🔄 Loading embedding model (API)...")
    model = HuggingFaceInferenceAPIEmbeddings(
        api_key=os.getenv("HF_TOKEN"),
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print("✅ Embedding model loaded")
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
        self.llm = get_llm()
        self.embeddings = get_embeddings()
        self.supabase: Client = get_supabase()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful tax and financial assistant for Concierge AI.
            Answer questions accurately using the provided context and conversation history.
            
            Guidelines:
            - Use conversation history to understand context and follow-up questions
            - Be concise but thorough
            - If you're not confident, say so
            - Always cite sources using [Source: <source_name>] format
            - For complex scenarios, recommend connecting with an expert"""),
            ("user", """Conversation History:
{conversation_history}

Context documents:
{context}

Current Question: {query}

Provide a helpful answer that considers the conversation history and cites sources.""")
        ])
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 5) -> str:
        """Retrieve recent conversation history"""
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
        """Retrieve relevant documents using vector similarity search"""
        try:
            # Generate query embedding using HuggingFace Inference API
            # Returns list of floats directly
            query_embedding = self.embeddings.embed_query(query)
            
            # Search using pgvector function
            result = self.supabase.rpc(
                'match_knowledge_documents',
                {
                    'query_embedding': query_embedding,
                    'match_count': k,
                    'match_threshold': 0.4
                }
            ).execute()
            
            return result.data if result.data else []
        
        except Exception as e:
            print(f"⚠️ Document retrieval error: {e}")
            return []
    
    async def generate_answer(self, query: str, conversation_id: str = None) -> Dict:
        """Generate RAG-based answer with conversation memory"""
        
        # Get conversation history
        conversation_history = await self.get_conversation_history(conversation_id)
        
        # Retrieve relevant documents
        documents = await self.retrieve_documents(query)
        
        if not documents or len(documents) == 0:
            return {
                "answer": "I don't have enough information in my knowledge base to answer this question confidently. Let me connect you with an expert who can provide personalized guidance.",
                "sources": [],
                "confidence": 0.3
            }
        
        # Format context from retrieved documents
        context = "\n\n".join([
            f"[Source: {doc['title']}]\n{doc['content']}\n(Relevance: {doc.get('similarity', 0):.2f})"
            for doc in documents
        ])
        
        try:
            # Generate answer using LLM
            chain = self.prompt | self.llm
            response = chain.invoke({
                "conversation_history": conversation_history,
                "context": context,
                "query": query
            })
            
            # Calculate confidence based on document similarity scores
            avg_similarity = sum(doc.get('similarity', 0) for doc in documents) / len(documents)
            confidence = min(0.95, avg_similarity * 1.2)
            
            # Check if answer suggests expert consultation
            answer_lower = response.content.lower()
            if any(phrase in answer_lower for phrase in [
                'consult an expert', 'speak with an expert', 'expert can help',
                'recommend talking to', 'personalized advice', 'individual circumstances'
            ]):
                confidence = min(confidence, 0.7)
            
            return {
                "answer": response.content,
                "sources": [
                    {"title": doc['title'], "source": doc.get('source', 'Internal'), "similarity": doc.get('similarity', 0)}
                    for doc in documents
                ],
                "confidence": round(confidence, 2)
            }
        
        except Exception as e:
            print(f"⚠️ LLM generation error: {e}")
            return {
                "answer": "I encountered an issue generating a response. Let me connect you with an expert who can help.",
                "sources": [],
                "confidence": 0.2
            }

# Singleton instance
rag_service = RAGService()

# Pre-warm the service
try:
    print("🔥 Pre-warming RAG service...")
    _ = get_embeddings().embed_query("warmup query")
    print("✅ RAG service ready")
except Exception as e:
    print(f"⚠️ RAG pre-warm warning: {e}")
