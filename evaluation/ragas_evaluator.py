"""
RAGAS Integration for Expert-Level RAG Evaluation
Measures: Context Precision, Context Recall, Context Relevancy, Faithfulness, Answer Relevancy
"""
import os
import uuid
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    ContextRelevance,
    faithfulness,
    answer_relevancy
)
import litellm

# Explicitly set model names for RAGAS
CONTEXT_RELEVANCE = ContextRelevance()


class RAGASEvaluator:
    """
    Evaluates RAG quality using RAGAS metrics.
    Industry-standard evaluation for production RAG systems.
    """
    
    def __init__(self):
        self.metrics = [
            context_precision,    # Are top docs most relevant?
            context_recall,       # Did we find all needed info?
            CONTEXT_RELEVANCE,    # How much retrieved content is relevant?
            faithfulness,         # Is answer grounded in context?
            answer_relevancy      # Does answer address the question?
        ]
        
        # Initialize embeddings immediately for accessibility
        try:
            from services.hf_embeddings import HuggingFaceEmbeddings
            self.evaluator_embeddings = HuggingFaceEmbeddings(
                model="sentence-transformers/all-MiniLM-L6-v2",
                api_token=os.getenv("HF_TOKEN")
            )
        except ImportError:
            print("⚠️ Could not import HuggingFaceEmbeddings - services module not found?")
            self.evaluator_embeddings = None
    
    async def evaluate_rag_quality(self, test_cases: list) -> dict:
        """
        Evaluate RAG quality across test cases using RAGAS.
        
        Args:
            test_cases: List of dicts with:
                - question: User query
                - answer: Generated answer
                - contexts: List of retrieved document texts
                - ground_truth: Expected answer (optional)
        
        Returns:
            {
                "context_precision": float,
                "context_recall": float,
                "context_relevancy": float,
                "faithfulness": float,
                "answer_relevancy": float,
                "overall_score": float
            }
        """
        
        # Convert to RAGAS dataset format
        dataset_dict = {
            "question": [],
            "answer": [],
            "contexts": [],
            "ground_truth": []
        }
        
        for case in test_cases:
            dataset_dict["question"].append(case["question"])
            dataset_dict["answer"].append(case["answer"])
            dataset_dict["contexts"].append(case["contexts"])
            dataset_dict["ground_truth"].append(case.get("ground_truth", ""))
        
        dataset = Dataset.from_dict(dataset_dict)
        
        # Use ChatLiteLLM with fallbacks for evaluation
        from langchain_community.chat_models import ChatLiteLLM
        import litellm
        import logging
        
        # Silence verbose litellm logging as requested
        litellm.set_verbose = False
        litellm.suppress_handler_errors = True
        litellm.add_status_to_exception = False
        litellm.telemetry = False
        logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
        
        # Use ChatLiteLLM directly (standard community import)
        from langchain_community.chat_models import ChatLiteLLM
        
        # Hard-default to Lite model to prevent Pro/Exp rate limits
        default_model = "gemini/gemini-2.5-flash-lite-preview-09-2025"
        model_name = os.getenv("RAGAS_EVALUATOR_MODEL", default_model)
        
        print(f"⚖️ RAGAS Judge Model: {model_name}")
        
        llm = ChatLiteLLM(
            model=model_name,
            temperature=0
        )
        
        # Wrap the LLM for RAGAS 0.4+
        from ragas.llms import LangchainLLMWrapper
        evaluator_llm = LangchainLLMWrapper(llm)
        
        # Run RAGAS evaluation sequentially with 60s delay per item
        # This is SLOW but necessary for free tier rate limits
        all_scores = []
        import asyncio
        import pandas as pd
        
        print("\n🐢 Running RAGAS in SLOW mode (60s delay/item)...")
        
        for i, item in enumerate(dataset):
            print(f"   Evaluating item {i+1}/{len(dataset)}...")
            
            # Create single-item dataset
            single_ds = Dataset.from_list([item])
            
            try:
                result = evaluate(
                    single_ds,
                    metrics=self.metrics,
                    llm=evaluator_llm,
                    embeddings=self.evaluator_embeddings,
                    raise_exceptions=False
                )
                df = result.to_pandas()
                all_scores.append(df)
                
            except Exception as e:
                print(f"   ⚠️ Failed item {i+1}: {e}")
            
            # Sleep 60s between items (except last one)
            if i < len(dataset) - 1:
                print("   ⏳ Sleeping 60s...")
                await asyncio.sleep(60)
        
        # Merge all results
        if not all_scores:
            return {}
            
        combined_df = pd.concat(all_scores)
        print(f"📊 Ragas Result Columns: {combined_df.columns.tolist()}")
        
        # Extract mean scores
        try:
            scores = {
                "context_precision": float(combined_df["context_precision"].mean()) if "context_precision" in combined_df.columns else 0.0,
                "context_recall": float(combined_df["context_recall"].mean()) if "context_recall" in combined_df.columns else 0.0,
                "context_relevancy": float(combined_df.get("context_relevancy", combined_df.get("nv_context_relevance", 0.0)).mean()),
                "faithfulness": float(combined_df["faithfulness"].mean()) if "faithfulness" in combined_df.columns else 0.0,
                "answer_relevancy": float(combined_df["answer_relevancy"].mean()) if "answer_relevancy" in combined_df.columns else 0.0
            }
        except Exception as e:
            print(f"Warning: Could not extract RAGAS scores: {e}")
            scores = {}

        
        # Add overall score
        scores["overall_score"] = sum(v for v in scores.values() if isinstance(v, (int, float))) / 5.0
        
        return scores
    
    def interpret_scores(self, scores: dict) -> dict:
        """
        Interpret RAGAS scores against production thresholds.
        
        Returns:
            {
                "context_precision": {"score": 0.85, "status": "PASS", "target": 0.80},
                ...
            }
        """
        thresholds = {
            "context_precision": 0.80,
            "context_recall": 0.85,
            "context_relevancy": 0.70,
            "faithfulness": 0.90,  # Higher for tax domain (high risk)
            "answer_relevancy": 0.85
        }
        
        interpretation = {}
        
        for metric, score in scores.items():
            if metric == "overall_score":
                continue
            
            target = thresholds.get(metric, 0.80)
            status = "PASS" if score >= target else "FAIL"
            
            interpretation[metric] = {
                "score": round(score, 3),
                "target": target,
                "status": status,
                "gap": round(score - target, 3)
            }
        
        return interpretation


def format_ragas_report(scores: dict, interpretation: dict) -> str:
    """Format RAGAS results for console output"""
    
    report = "\n" + "="*60 + "\n"
    report += "RAGAS EVALUATION - Industry Standard RAG Metrics\n"
    report += "="*60 + "\n\n"
    
    report += "📊 RETRIEVAL QUALITY:\n"
    report += f"   Context Precision:  {interpretation['context_precision']['score']:.3f} "
    report += f"({'✅ PASS' if interpretation['context_precision']['status'] == 'PASS' else '❌ FAIL'}) "
    report += f"(target: {interpretation['context_precision']['target']})\n"
    
    report += f"   Context Recall:     {interpretation['context_recall']['score']:.3f} "
    report += f"({'✅ PASS' if interpretation['context_recall']['status'] == 'PASS' else '❌ FAIL'}) "
    report += f"(target: {interpretation['context_recall']['target']})\n"
    
    report += f"   Context Relevance:  {interpretation['context_relevancy']['score']:.3f} "
    report += f"({'✅ PASS' if interpretation['context_relevancy']['status'] == 'PASS' else '❌ FAIL'}) "
    report += f"(target: {interpretation['context_relevancy']['target']})\n\n"
    
    report += "📝 GENERATION QUALITY:\n"
    report += f"   Faithfulness:       {interpretation['faithfulness']['score']:.3f} "
    report += f"({'✅ PASS' if interpretation['faithfulness']['status'] == 'PASS' else '❌ FAIL'}) "
    report += f"(target: {interpretation['faithfulness']['target']})\n"
    
    report += f"   Answer Relevancy:   {interpretation['answer_relevancy']['score']:.3f} "
    report += f"({'✅ PASS' if interpretation['answer_relevancy']['status'] == 'PASS' else '❌ FAIL'}) "
    report += f"(target: {interpretation['answer_relevancy']['target']})\n\n"
    
    # Overall assessment
    passed = sum(1 for m in interpretation.values() if m['status'] == 'PASS')
    total = len(interpretation)
    
    report += f"🎯 OVERALL: {passed}/{total} metrics passed\n"
    
    if scores.get("overall_score", 0) >= 0.85:
        report += "   Rating: 🌟 EXPERT LEVEL (production-ready)\n"
    elif scores.get("overall_score", 0) >= 0.75:
        report += "   Rating: ✨ STRONG (production-worthy)\n"
    elif scores.get("overall_score", 0) >= 0.65:
        report += "   Rating: 👍 GOOD (needs minor improvements)\n"
    else:
        report += "   Rating: ⚠️  NEEDS WORK (not production-ready)\n"
    
    report += "="*60 + "\n"
    
    return report
