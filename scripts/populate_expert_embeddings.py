from sentence_transformers import SentenceTransformer
from supabase import create_client
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
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

print("👤 Fetching experts...")
experts = supabase.table('experts').select('*').execute()
print(f"Found {len(experts.data)} experts")

for i, expert in enumerate(experts.data, 1):
    print(f"\n[{i}/{len(experts.data)}] Processing: {expert['name']}")
    
    # Create a rich text representation for embedding
    # Combine name, bio, and specialties for better semantic matching
    text_to_embed = f"{expert['name']} - {expert['bio']}. Specialties: {', '.join(expert['specialties'])}"
    
    print(f"  ℹ️ Embedding text: {text_to_embed}")
    
    # Generate embedding
    embedding = model.encode(text_to_embed).tolist()
    print(f"  ✓ Generated {len(embedding)}-dimensional embedding")
    
    # Update expert
    supabase.table('experts').update({
        'expertise_embedding': embedding
    }).eq('id', expert['id']).execute()
    print(f"  ✓ Updated in database")

print("\n" + "="*50)
print("✅ All expert embeddings generated successfully!")
print("💰 Total cost: $0.00")
print("="*50)
