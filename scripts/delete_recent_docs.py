import os
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(dotenv_path=".env.local")

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

def delete_recent_docs():
    print("🧹 Starting cleanup of recent documents...")
    
    # Calculate cutoff time (1 hour ago)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
    cutoff_iso = cutoff_time.isoformat()
    
    print(f"🕒 Deleting documents created after: {cutoff_iso}")
    
    try:
        # First count how many
        response = supabase.table('knowledge_documents')\
            .select('id', count='exact')\
            .gt('created_at', cutoff_iso)\
            .execute()
            
        count = response.count
        print(f"📊 Found {count} documents to delete.")
        
        if count == 0:
            print("✅ No recent documents found to delete.")
            return

        # Delete in batches if needed, but for now just try delete
        # Supabase python client might not support delete without filters, verifying...
        # We will delete by ID blocks or just use the filter
        
        response = supabase.table('knowledge_documents')\
            .delete()\
            .gt('created_at', cutoff_iso)\
            .execute()
            
        print(f"✅ Successfully deleted recent documents.")
        
    except Exception as e:
        print(f"❌ Error during deletion: {e}")

if __name__ == "__main__":
    delete_recent_docs()
