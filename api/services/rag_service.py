from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpointEmbeddings
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
    model = HuggingFaceEndpointEmbeddings(
        huggingfacehub_api_token=os.getenv("HF_TOKEN"),
        model="sentence-transformers/all-MiniLM-L6-v2"
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
            - Be EXTREMELY concise and easy to understand
            - Use bullet points for lists or steps
            - Avoid long paragraphs and complex jargon
            - If you're not confident, say so
            - Cite sources using [1], [2] format corresponding to the source numbers
            - Do NOT list the full source titles at the end (the UI will handle this)
            - For complex scenarios, recommend connecting with an expert"""),
            ("user", """Conversation History:
{conversation_history}

Context documents:
{context}

Current Question: {query}

Provide a helpful answer that considers the conversation history and cites sources.""")
        ])
        
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", """Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""),
            ("user", """Chat History:
{conversation_history}

User Question: {query}

Standalone Question:""")
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
        documents = await self.retrieve_documents(standalone_query)
        
        if not documents or len(documents) == 0:
            return {
                "answer": "I don't have enough information in my knowledge base to answer this question confidently. Let me connect you with an expert who can provide personalized guidance.",
                "sources": [],
                "confidence": 0.3
            }
        
        # Format context from retrieved documents
        context = "\n\n".join([
            f"[Source {i+1}: {doc['title']}]\n{doc['content']}\n(Relevance: {doc.get('similarity', 0):.2f})"
            for i, doc in enumerate(documents)
        ])
        
        try:
            # Generate answer using LLM
            chain = self.prompt | self.llm
            response = chain.invoke({
                "conversation_history": conversation_history,
                "context": context,
                "query": query
            })
            
            # Calculate confidence based on MAX document similarity
            # Average penalizes having extra context. Max represents the best match found.
            max_similarity = max(doc.get('similarity', 0) for doc in documents)
            # Boost factor for MiniLM (which tends to have lower raw cosine scores)
            confidence = min(0.95, max_similarity * 1.5)
            
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

