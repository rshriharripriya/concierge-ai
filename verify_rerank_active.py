
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from dotenv import load_dotenv
load_dotenv(".env.local")

import services.reranker as reranker_service

async def main():
    print("🚀 Initializing reranker...")
    reranker_service.initialize()
    
    if not reranker_service.service_instance:
        print("❌ Service instance is None")
        return
        
    service_instance = reranker_service.service_instance

    print(f"Service Enabled: {service_instance.enabled}")
    if not service_instance.enabled:
        print(f"Skipping test (Reranker disabled)")
        return

    # Dummy documents
    docs = [
        {"content": "The capital of France is Paris.", "id": 1},
        {"content": "Apples are delicious fruits.", "id": 2},
        {"content": "The Eiffel Tower is in Paris.", "id": 3},
        {"content": "Python is a programming language.", "id": 4}
    ]
    query = "What is the capital of France?"
    
    print("\n🧪 Testing reranking...")
    reranked = await service_instance.rerank(query, docs, top_n=2)
    
    print(f"Received {len(reranked)} results:")
    for doc in reranked:
        print(f" - {doc['content']} (Score: {doc.get('rerank_score')})")

    # Assertions
    if len(reranked) != 2:
        print("❌ Expected 2 results")
    if reranked[0]['id'] not in [1, 3]:
        print("❌ Top result should be about Paris")
    if 'rerank_score' not in reranked[0]:
        print("❌ Rerank score missing")
    else:
        print("\n✅ Reranker working correctly!")

if __name__ == "__main__":
    asyncio.run(main())
