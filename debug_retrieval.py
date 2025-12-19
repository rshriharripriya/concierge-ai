
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(dotenv_path='.env.local')

from api.services.hf_embeddings import HuggingFaceEmbeddings
from supabase import create_client

async def debug_retrieval():
    print("🔍 Debugging Retrieval for 'Standard Deduction 2024'...")
    
    # 1. Setup
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    embeddings = HuggingFaceEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        api_token=os.getenv("HF_TOKEN")
    )
    
    query = "What is the standard deduction for 2024?"
    print(f"\n📝 Query: {query}")
    
    # 2. Embed
    query_vec = embeddings.embed_query(query)
    print(f"✅ Embedded query (dim: {len(query_vec)})")
    
    # 3. Search
    print("🔎 Searching vector store...")
    result = supabase.rpc(
        'match_knowledge_documents',
        {
            'query_embedding': query_vec,
            'match_count': 5,
            'match_threshold': 0.3
        }
    ).execute()
    
    # 4. Analyze Results
    if not result.data:
        print("❌ No matches found!")
        return

    print(f"✅ Found {len(result.data)} matches:\n")
    for i, doc in enumerate(result.data):
        print(f"--- Result {i+1} (Sim: {doc['similarity']:.3f}) ---")
        print(f"Title: {doc['title']}")
        print(f"Chunk Preview: {doc['content'][:150]}...")
        if "2024" in doc['content']:
            print("🎯 HIT: Contains '2024'")
        else:
            print("⚠️ MISS: No '2024' found")
        print("\n")

if __name__ == "__main__":
    asyncio.run(debug_retrieval())
