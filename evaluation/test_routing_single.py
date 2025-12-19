
import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add parent path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api'))

# Load env variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env.local')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded .env.local from {env_path}")
else:
    print(f"⚠️ .env.local not found at {env_path}")

async def test_routing():
    print("🚀 Testing LLM Router Isolation...")
    
    # Enable LiteLLM verbose logging
    import litellm
    litellm.set_verbose = True
    
    from api.services import llm_router
    
    # Force initialize
    llm_router.initialize()
    router = llm_router.service_instance
    
    test_query = "What is the standard deduction for 2024?"
    print(f"\n📝 Query: {test_query}")
    print(f"🤖 Using Model: {os.getenv('LLM_ROUTER_MODEL')}")
    print(f"🔄 Fallbacks: {os.getenv('LLM_ROUTER_FALLBACKS')}")
    
    try:
        result = await router.route(test_query)
        print("\n✅ Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_routing())
