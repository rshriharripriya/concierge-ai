import asyncio
import sys
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Add current directory to path
# Add backend directory to path so 'services' package is found
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from services import rag_service

async def test_temporal():
    """Test temporal ranking in hybrid retrieval."""
    print("🚀 Initializing RAG service...")
    rag_service.initialize()
    
    retriever = rag_service.service_instance.retriever
    
    if retriever is None:
        print("❌ Hybrid retriever not initialized. Check your .env.local configuration.")
        return
    
    print(f"   use_temporal={retriever.use_temporal}")
    print(f"   base_recency_weight={retriever.base_recency_weight}")
    
    test_queries = [
        "What is the standard deduction for this year?",   # Should favor 2026
        "What was the standard deduction last year?",       # Should favor 2025
        "What was the standard deduction in 2023?",         # Should favor 2023
        "Can I deduct home office expenses?",               # No year - default recency
        "what is the std deduction this year? for az?", 

    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        
        # Show what year the extractor detects
        target_year = retriever._extract_target_year(query)
        print(f"Detected target year: {target_year}")
        print(f"{'='*80}")
        
        results = await retriever.retrieve(query, k=5)
        
        for i, doc in enumerate(results[:3], 1):
            metadata = doc.get('metadata', {}) or {}
            title = doc.get('title', 'No title')[:80]
            tax_years = metadata.get('tax_years', 'N/A')
            primary_year = metadata.get('primary_tax_year', 'N/A')
            temporal = doc.get('temporal_score', 'N/A')
            rrf = doc.get('rrf_score', 'N/A')
            final = doc.get('final_score', doc.get('hybrid_score', 'N/A'))
            
            print(f"\n  {i}. {title}")
            print(f"     Tax Years: {tax_years}")
            print(f"     Primary Year: {primary_year}")
            
            # Format scores safely
            if isinstance(temporal, (int, float)):
                print(f"     Temporal Score: {temporal:.3f}")
            else:
                print(f"     Temporal Score: {temporal}")
            
            if isinstance(rrf, (int, float)):
                print(f"     RRF Score: {rrf:.3f}")
            else:
                print(f"     RRF Score: {rrf}")
            
            if isinstance(final, (int, float)):
                print(f"     Final Score: {final:.3f}")
            else:
                print(f"     Final Score: {final}")

if __name__ == "__main__":
    asyncio.run(test_temporal())
