"""
Generate embeddings for expert specialties and update database.
This allows semantic matching between user queries and expert specializations.
"""
import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment
load_dotenv('.env.local')

# Initialize
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

# Expert data with specialties
experts_data = [
    # Female experts (10)
    {"email": "emily@concierge.ai", "text": "bookkeeping QuickBooks payroll accounting financial records small business"},
    {"email": "jennifer@concierge.ai", "text": "estate planning trusts inheritance wills tax minimization family wealth"},
    {"email": "sarah@concierge.ai", "text": "CPA small business tax Schedule C deductions startup LLC S-corp"},
    {"email": "amanda@concierge.ai", "text": "divorce alimony child support filing status marriage tax family law"},
    {"email": "lisa@concierge.ai", "text": "financial planning cash flow budgeting business finance advisor"},
    {"email": "patricia@concierge.ai", "text": "healthcare medical deductions HSA FSA physician doctor tax"},
    {"email": "nina@concierge.ai", "text": "freelance gig economy 1099 self-employed estimated taxes quarterly"},
    {"email": "rachel@concierge.ai", "text": "nonprofit 501c3 charitable donations tax-exempt organizations foundation"},
    {"email": "katherine@concierge.ai", "text": "education 529 plans student loans scholarships education credits tuition"},
    {"email": "michelle@concierge.ai", "text": "senior tax Social Security Medicare RMD retirement elderly retiree"},
    
    # Male experts (10)
    {"email": "david@concierge.ai", "text": "international tax foreign income expat FBAR FATCA overseas"},
    {"email": "michael@concierge.ai", "text": "real estate 1031 exchange rental property REITs landlord depreciation"},
    {"email": "alex@concierge.ai", "text": "startup equity compensation stock options ISO NSO venture capital RSU"},
    {"email": "marcus@concierge.ai", "text": "cryptocurrency Bitcoin capital gains trading NFT DeFi blockchain"},
    {"email": "james@concierge.ai", "text": "retirement 401k IRA Roth conversions pension withdrawal RMD"},
    {"email": "robert@concierge.ai", "text": "multi-state tax apportionment remote work state residency nexus"},
    {"email": "carlos@concierge.ai", "text": "IRS audit tax resolution representation appeals defense controversy"},
    {"email": "nathan@concierge.ai", "text": "manufacturing cost segregation R&D credits research development production"},
    {"email": "thomas@concierge.ai", "text": "agriculture farm tax conservation easements farming ranching crops"},
    {"email": "kevin@concierge.ai", "text": "e-commerce sales tax nexus online seller Shopify Amazon Etsy"}
]

print("🔄 Generating embeddings for expert specialties...")

for expert in experts_data:
    # Generate embedding
    embedding = embeddings.embed_query(expert["text"])
    
    # Update database
    result = supabase.table('experts').update({
        'expertise_embedding': embedding
    }).eq('email', expert['email']).execute()
    
    print(f"✅ Updated {expert['email']}")

print("\n✅ All expert embeddings generated successfully!")
print("Experts can now be semantically matched to user queries.")
