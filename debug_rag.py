
import os
import asyncio
from dotenv import load_dotenv
import litellm

# Load env safely
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.local')
load_dotenv(dotenv_path=env_path)

rag_model = os.getenv("RAG_MODEL", "NOT_SET")
print(f"RAG Model: {rag_model}")

print("--- Testing RAG Model ---")
try:
    response = litellm.completion(
        model=rag_model,
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=100
    )
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print(f"❌ Failed: {e}")
