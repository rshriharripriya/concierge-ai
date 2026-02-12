
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(dotenv_path='.env.local')

from backend.services.hf_embeddings import HuggingFaceEmbeddings
from supabase import create_client

async def debug_retrieval():
    print("🔍 Debugging Retrieval for 'Standard Deduction 2025'...")
    
    # 1. Setup
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    embeddings = HuggingFaceEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        api_token=os.getenv("HF_TOKEN")
    )
    
    query = "Earned Income Credit"
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
            'match_count': 20,
            'match_threshold': 0.3
        }
    ).execute()
    
    # 4. Test Hybrid Search RPC
    print("🔎 Testing Hybrid Search RPC...")
    try:
        hybrid_result = supabase.rpc(
            'hybrid_search_knowledge_documents',
            {
                'query_text': query,
                'query_embedding': query_vec,
                'match_count': 10,
                'bm25_weight': 0.5,
                'vector_weight': 0.5
            }
        ).execute()
        print(f"✅ Hybrid Search worked! Found {len(hybrid_result.data)} matches.")
        for i, doc in enumerate(hybrid_result.data):
             source = doc.get('metadata', {}).get('source') if doc.get('metadata') else doc.get('source')
             title = doc.get('title', 'Unknown')
             score = doc.get('combined_score', 0)
             
             if source and "rp-24-40" in source:
                 print(f"🎯 Hybrid HIT: {title} (Score: {score:.3f})")
             else:
                 print(f"   Rank {i+1}: {title[:40]}... (Score: {score:.3f})")
    except Exception as e:
        print(f"❌ Hybrid Search Failed: {e}")
        
    print("\n✅ Setup Analysis Complete.")

if __name__ == "__main__":
    asyncio.run(debug_retrieval())
