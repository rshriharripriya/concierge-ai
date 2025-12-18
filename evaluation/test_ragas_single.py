
import asyncio
import os
import sys

# Add parent and api directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api'))

from dotenv import load_dotenv
# Load from project root .env.local
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env.local')
load_dotenv(dotenv_path=env_path)

async def test_ragas_single():
    print("🚀 Testing RAGAS on a single sample...")
    
    # Enable verbose logging to see LLM inputs/outputs
    import langchain
    langchain.debug = True
    print("📋 LangChain Debug Mode Enabled (prompts will appear below)")
    
    try:
        from evaluation.ragas_evaluator import RAGASEvaluator, format_ragas_report
    except ImportError as e:
        print(f"❌ Failed to import RAGASEvaluator: {e}")
        print("💡 Try: pip install datasets ragas")
        return

    # 1. Initialize Evaluator
    try:
        evaluator = RAGASEvaluator()
        print("✅ Evaluator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Evaluator: {e}")
        return
    
    # 1.5 Test Embeddings Manually
    print("🔌 Testing Embedding API connection...")
    try:
        sample_embed = evaluator.evaluator_embeddings.embed_query("test")
        print(f"✅ Embeddings working! Vector length: {len(sample_embed)}")
        if all(x == 0 for x in sample_embed):
            print("⚠️ WARNING: Embeddings returned all zeros!")
    except Exception as e:
        print(f"❌ Embedding API FAILED: {e}")
        return

    # 2. Create a dummy test case
    # 2. Create a dummy test case with COMPREHENSIVE context to fix Faithfulness
    # RAGAS penalizes answers that contain info not in the context!
    test_case = [{
        "question": "What is the standard deduction for 2024?",
        "answer": "The standard deduction for 2024 depends on your filing status.\n\nFor single filers: $14,600\nFor married filing jointly: $29,200\nFor married filing separately: $14,600\nFor head of household: $21,900\n\nTo give you an exact number, are you filing single, married, or head of household?",
        "contexts": [
            "IRS Revenue Procedure 2023-34: For tax year 2024, the standard deduction amounts are: $14,600 for Single or Married Filing Separately; $29,200 for Married Filing Jointly or Qualifying Surviving Spouse; $21,900 for Head of Household."
        ],
        "ground_truth": "The standard deduction for 2024 is $14,600 for single filers, $29,200 for married filing jointly, and $21,900 for head of household."
    }]
    
    # 3. Run Evaluation
    print("🐢 Running evaluation (expect delay due to rate limiting)...")
    try:
        scores = await evaluator.evaluate_rag_quality(test_case)
        
        # 4. Show Results
        print("\n✅ Results:")
        interpretation = evaluator.interpret_scores(scores)
        print(format_ragas_report(scores, interpretation))
    except Exception as e:
        print(f"❌ Evaluation FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ragas_single())
