import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.services import rag_service

async def test_context():
    print("🚀 Testing RAG Context Awareness...")
    
    # Initialize service
    rag_service.initialize()
    
    # Simulate conversation history
    history = """User: Is crypto taxable?
Assistant: Yes, crypto is treated as property and gains are taxable."""
    
    query = "what about bitcoin?"
    
    # 1. Test Contextualization
    print("\n🔄 Testing Query Contextualization...")
    standalone = await rag_service.service_instance.contextualize_query(query, history)
    print(f"Original: '{query}'")
    print(f"Standalone: '{standalone}'")
    
    if "bitcoin" in standalone.lower() and ("tax" in standalone.lower() or "taxable" in standalone.lower()):
        print("✅ Contextualization successful")
    else:
        print("❌ Contextualization failed (expected 'tax' reference)")

    # 2. Test Retrieval with Standalone Query
    print("\n🔍 Retrieving documents for standalone query...")
    docs = await rag_service.service_instance.retrieve_documents(standalone)
    for i, doc in enumerate(docs):
        print(f"{i+1}. {doc['title']} (Similarity: {doc['similarity']:.3f})")

    # 3. Test Generation (Conciseness)
    print("\n🤖 Generating answer (checking conciseness)...")
    # We mock the history retrieval by just passing the query, but in a real app 
    # the history comes from DB. Here we just want to see the style.
    # To properly test generate_answer with history, we'd need to mock get_conversation_history
    # or insert into DB. For now, let's just check the prompt output style with a direct invoke.
    
    # Let's just run generate_answer with a dummy conversation_id that returns empty history
    # effectively testing the prompt style on a fresh query
    result = await rag_service.service_instance.generate_answer("How are international students taxed on scholarships?")
    print(f"\nAnswer:\n{result['answer']}")
    
    if "-" in result['answer'] or "*" in result['answer']:
        print("✅ Answer uses bullet points")
    else:
        print("⚠️ Answer might not use bullet points")

if __name__ == "__main__":
    asyncio.run(test_context())
