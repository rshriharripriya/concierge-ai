
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(dotenv_path='.env.local')

def check_db():
    print("🔍 Checking Supabase 'knowledge_documents' table...")
    
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    try:
        # Get count
        count = supabase.table('knowledge_documents').select('*', count='exact', head=True).execute()
        print(f"📊 Total documents: {count.count}")
        
        # Get latest 5 insertions
        print("\n🕒 Latest 5 documents:")
        response = supabase.table('knowledge_documents')\
            .select('id, title, created_at, content')\
            .order('created_at', desc=True)\
            .limit(5)\
            .execute()
            
        for doc in response.data:
            print(f"[{doc['created_at']}] {doc['title']}")
            print(f"   Preview: {doc['content'][:100]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_db()
