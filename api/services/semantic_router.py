from semantic_router import Route, SemanticRouter
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from typing import List, Dict, Any
from functools import lru_cache
import os

class APIEncoder:
    """Custom encoder using HuggingFace Inference API via LangChain"""
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=os.getenv("HF_TOKEN"),
            model_name=model_name
        )
        self.score_threshold = 0.3 # Default threshold
        self.name = model_name
        self.type = "api"

    def __call__(self, docs: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(docs)

@lru_cache(maxsize=1)
def get_semantic_router():
    """Cached router instance to survive cold starts"""
    routes = [
        Route(
            name="simple_tax",
            utterances=[
                "What is the standard deduction?",
                "What is the standard deduction for 2024?",
                "What is the std deduction?",
                "std deduction 2024",
                "When is the tax filing deadline?",
                "How do I claim deductions?",
                "What forms do I need?",
                "Can I file jointly?",
                "What is a W-2 form?",
                "How do I get a tax refund?",
                "Am I eligible for the Earned Income Tax Credit?",
                "What are the tax brackets for 2024?",
                "Can I deduct my home office expenses?",
                "How do I file for an extension?",
            ]
        ),
        Route(
            name="complex_tax",
            utterances=[
                "Capital gains from crypto staking",
                "Foreign tax credit calculations",
                "Section 1031 exchange requirements",
                "Qualified business income deduction",
                "Multi-state tax allocation",
                "International tax treaties",
                "Partnership K-1 distributions",
            ]
        ),
        Route(
            name="bookkeeping",
            utterances=[
                "How do I reconcile accounts?",
                "QuickBooks setup help",
                "Categorizing expenses",
                "Invoice management",
                "Payroll processing",
                "Cash flow statements",
                "Chart of accounts setup",
            ]
        ),
        Route(
            name="urgent",
            utterances=[
                "IRS audit notice",
                "Payment deadline today",
                "Account locked",
                "Emergency tax issue",
                "Urgent deadline approaching",
                "Penalty notice received",
                "Payment plan needed now",
            ]
        ),
        Route(
            name="general",
            utterances=[
                "General inquiry",
                "Need information",
                "Have a question",
                "Looking for help",
                "Can you assist me?",
            ]
        )
    ]
    
    # Use API encoder instead of local
    print("🔄 Loading API encoder...")
    encoder = APIEncoder()
    print("✅ Encoder loaded")
    
    return SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")

class SemanticRouterService:
    def __init__(self):
        self.router = get_semantic_router()
    
    def classify_intent(self, query: str) -> Dict:
        """Classify user query into intent categories"""
        route = self.router(query)
        return {
            "intent": route.name if route and route.name else "general",
            "confidence": route.similarity_score if route else 0.5
        }

# Singleton instance
semantic_router = SemanticRouterService()

# Pre-warm the router
try:
    print("🔥 Pre-warming semantic router...")
    _ = semantic_router.classify_intent("test query")
    print("✅ Semantic router initialized")
except Exception as e:
    print(f"⚠️ Router initialization warning: {e}")
