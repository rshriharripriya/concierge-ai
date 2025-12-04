import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import uuid

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in .env.local")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

# Initialize Embedding Model (API)
print("🔄 Loading embedding model (API)...")
model = HuggingFaceEndpointEmbeddings(
    huggingfacehub_api_token=os.getenv("HF_TOKEN"),
    model="sentence-transformers/all-MiniLM-L6-v2"
)
print("✅ Model loaded")


import traceback

def ingest_documents(documents):
    """
    Ingest a list of documents into the vector database.
    Each document should be a dict with 'title' and 'content'.
    """
    print(f"🚀 Starting ingestion of {len(documents)} documents...")
    
    # Pre-flight check
    try:
        print("🔍 Checking 'knowledge_documents' table schema...")
        response = supabase.table('knowledge_documents').select('*').limit(1).execute()
        if response.data:
            print(f"✅ Table columns: {list(response.data[0].keys())}")
        else:
            print("✅ Table exists but is empty (cannot infer columns)")
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        print("⚠️ The 'knowledge_documents' table might not exist. Please check your Supabase schema.")
    
    for doc in documents:
        try:
            print(f"Processing: {doc['title']}")
            
            # Generate embedding
            embedding = model.embed_query(doc['content'])
            
            # Prepare data payload
            data = {
                "content": doc['content'],
                "title": doc['title'],
                "source": "manual_ingest",
                "metadata": {"title": doc['title'], "source": "manual_ingest"},
                "content_embedding": embedding
            }
            
            # Insert into Supabase
            response = supabase.table('knowledge_documents').insert(data).execute()
            print(f"✅ Inserted: {doc['title']}")
            
        except Exception as e:
            print(f"❌ Failed to insert {doc['title']}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    # Files to ingest
    files_to_ingest = [
        "knowledge_data/knowledge_international_students.txt",
        "knowledge_data/knowledge_investments.txt"
    ]
    
    documents = []
    
    for file_path in files_to_ingest:
        try:
            # Handle path if running from scripts dir or root
            if not os.path.exists(file_path):
                # Try adding ../ if running from scripts dir
                if os.path.exists(f"../{file_path}"):
                    file_path = f"../{file_path}"
                elif os.path.exists(f"concierge-ai/{file_path}"):
                     file_path = f"concierge-ai/{file_path}"
            
            if not os.path.exists(file_path):
                print(f"⚠️ File not found: {file_path}")
                continue
                
            print(f"📖 Reading {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Create document object
            # Use filename as title, replacing underscores with spaces
            filename = os.path.basename(file_path)
            title = filename.replace('knowledge_', '').replace('.txt', '').replace('_', ' ').title()
            
            documents.append({
                "title": title,
                "content": content
            })
            
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")

    if documents:
        ingest_documents(documents)
    else:
        print("No documents found to ingest.")
