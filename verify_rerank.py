import asyncio
import os
import logging
import sys
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

load_dotenv('.env.local')
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

async def test_reranking():
    print("=" * 60)
    print("RERANKER DIAGNOSTIC TEST")
    print("=" * 60)
    
    print("\n1️⃣ Environment Variables:")
    print(f"   COHERE_API_KEY: {'✅ SET' if os.getenv('COHERE_API_KEY') else '❌ MISSING'}")
    print(f"   USE_RERANKING: {os.getenv('USE_RERANKING', 'not set')}")
    print(f"   RERANK_TOP_K: {os.getenv('RERANK_TOP_K', 'not set')}")
    print(f"   RERANK_FINAL_K: {os.getenv('RERANK_FINAL_K', 'not set')}")
    
    print("\n2️⃣ Initializing Services...")
    
    # Test reranker in isolation first
    from api.services import reranker
    reranker.initialize()
    
    if reranker.service_instance:
        print(f"   ✅ Reranker instance created")
        print(f"   Enabled: {reranker.service_instance.enabled}")
        print(f"   Client: {reranker.service_instance.client}")
    else:
        print(f"   ❌ Reranker instance is None")
        return
    
    # Now test RAG service
    from api.services.rag_service import RAGService
    rag = RAGService()
    
    print(f"\n   RAG Service reranker reference: {rag.reranker}")
    if rag.reranker:
        print(f"   RAG reranker enabled: {rag.reranker.enabled}")
    
    print("\n3️⃣ Testing Query...")
    query = "What is Form 1040-NR?"
    print(f"   Query: {query}")
    print("-" * 60)
    
    result = await rag.generate_answer(query)
    
    print("-" * 60)
    print("\n4️⃣ Results:")
    print(f"   Sources returned: {len(result.get('sources', []))}")
    print(f"   Confidence: {result.get('confidence', 'N/A')}")
    
    print("\n   Top 3 sources:")
    for i, source in enumerate(result.get('sources', [])[:3], 1):
        print(f"   {i}. {source['title'][:60]}")
        print(f"      Similarity: {source.get('similarity', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test_reranking())
