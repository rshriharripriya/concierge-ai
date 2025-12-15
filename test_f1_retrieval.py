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
    print("🚀 Testing RAG Retrieval for F-1 student queries...")
    
    # Initialize service
    rag_service.initialize()
    
    queries = [
        "im an f1 student, i graduated may 2025, i dont have any income from then, do i pay taxes?",
        "i mean f1 international student",
        "i earn 3000 which tax bracket am i in"
    ]
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print('='*80)
        
        # Test retrieval
        docs = await rag_service.service_instance.retrieve_documents(query)
        
        if not docs:
            print("❌ No documents found")
        else:
            print(f"✅ Found {len(docs)} documents:")
            for i, doc in enumerate(docs, 1):
                print(f"\n  [{i}] {doc['title']}")
                print(f"      Similarity: {doc['similarity']:.3f}")
                print(f"      Preview: {doc['content'][:150]}...")
        
        # Test full generation
        result = await rag_service.service_instance.generate_answer(query)
        print(f"\n📊 Confidence: {result['confidence']}")
        print(f"📝 Answer length: {len(result['answer'])} chars")

if __name__ == "__main__":
    asyncio.run(test_retrieval())
