from sentence_transformers import SentenceTransformer
from supabase import create_client
import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(dotenv_path=env_path)

print("🔄 Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✅ Model loaded")

print("🔄 Connecting to Supabase...")
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
print("✅ Connected")

# Get all documents without embeddings
print("📄 Fetching documents...")
docs = supabase.table('knowledge_documents').select('*').execute()
print(f"Found {len(docs.data)} documents")

for i, doc in enumerate(docs.data, 1):
    print(f"\n[{i}/{len(docs.data)}] Processing: {doc['title']}")
    
    # Generate embedding (completely free!)
    embedding = model.encode(doc['content']).tolist()
    print(f"  ✓ Generated {len(embedding)}-dimensional embedding")
    
    # Update document
    supabase.table('knowledge_documents').update({
        'content_embedding': embedding
    }).eq('id', doc['id']).execute()
    print(f"  ✓ Updated in database")

print("\n" + "="*50)
print("✅ All embeddings generated successfully!")
print("💰 Total cost: $0.00")
print("="*50)
