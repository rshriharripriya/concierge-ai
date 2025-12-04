import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
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
model = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv("HF_TOKEN"),
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
print("✅ Model loaded")

def ingest_documents(documents):
    """
    Ingest a list of documents into the vector database.
    Each document should be a dict with 'title' and 'content'.
    """
    print(f"🚀 Starting ingestion of {len(documents)} documents...")
    
    for doc in documents:
        try:
            print(f"Processing: {doc['title']}")
            
            # Generate embedding
            embedding = model.embed_query(doc['content'])
            
            # Prepare data payload
            data = {
                "content": doc['content'],
                "metadata": {"title": doc['title'], "source": "manual_ingest"},
                "embedding": embedding
            }
            
            # Insert into Supabase
            # Note: The table name is 'documents' based on rag_service usage
            # We might need to adjust if the table schema requires specific columns
            # Assuming a standard pgvector setup with 'content', 'metadata', 'embedding'
            
            # Check if we need to match the exact schema expected by the RAG service
            # RAG service uses rpc 'match_knowledge_documents'
            # Let's try to insert into a 'documents' table. 
            # If it fails, we might need to check the schema.
            
            response = supabase.table('documents').insert(data).execute()
            print(f"✅ Inserted: {doc['title']}")
            
        except Exception as e:
            print(f"❌ Failed to insert {doc['title']}: {e}")

if __name__ == "__main__":
    # Example documents - Add your new knowledge here
    new_documents = [
        {
            "title": "Standard Deduction 2024",
            "content": """The standard deduction for the 2024 tax year is:
- Single or Married Filing Separately: $14,600
- Married Filing Jointly or Qualifying Surviving Spouse: $29,200
- Head of Household: $21,900

The standard deduction reduces the amount of income you are taxed on. You can choose to take the standard deduction or itemize your deductions, whichever lowers your tax bill the most."""
        },
        {
            "title": "Earned Income Tax Credit (EITC) 2024",
            "content": """For the 2024 tax year, the Earned Income Tax Credit (EITC) ranges from $632 to $7,830 depending on your filing status and the number of children you have. 
- No children: Max credit $632
- 1 child: Max credit $4,213
- 2 children: Max credit $6,960
- 3 or more children: Max credit $7,830

To qualify, you must have earned income under specific limits."""
        },
        {
            "title": "Tax Filing Deadline 2024",
            "content": """The deadline to file your 2023 federal income tax return is Monday, April 15, 2024. 
If you live in Maine or Massachusetts, you have until April 17, 2024, due to state holidays.
If you request an extension, your filing deadline is extended to October 15, 2024, but any taxes owed are still due by the April deadline."""
        }
    ]
    
    ingest_documents(new_documents)
