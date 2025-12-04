import asyncio
import sys
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.services import rag_service

async def test_retrieval():
    print("🚀 Testing RAG Retrieval for 'what about nft'...")
    
    # Initialize service
    rag_service.initialize()
    
    queries = ["what about nft", "how are nfts taxed", "nft taxation"]
    
    for query in queries:
        print(f"\n🚀 Testing query: '{query}'")
        
        # 1. Test raw retrieval
        print("🔍 Retrieving documents...")
        docs = await rag_service.service_instance.retrieve_documents(query)
        
        if not docs:
            print("   ❌ No documents found")
        
        for i, doc in enumerate(docs):
            print(f"   {i+1}. {doc['title']} (Similarity: {doc['similarity']:.3f})")

        # 2. Test full generation
        print("🤖 Generating answer...")
        result = await rag_service.service_instance.generate_answer(query)
        print(f"   Confidence: {result['confidence']}")

if __name__ == "__main__":
    asyncio.run(test_retrieval())
