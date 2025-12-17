"""
RAGAS Integration for Expert-Level RAG Evaluation
Measures: Context Precision, Context Recall, Context Relevancy, Faithfulness, Answer Relevancy
"""
import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    context_relevancy,
    faithfulness,
    answer_relevancy
)


class RAGASEvaluator:
    """
    Evaluates RAG quality using RAGAS metrics.
    Industry-standard evaluation for production RAG systems.
    """
    
    def __init__(self):
        self.metrics = [
            context_precision,    # Are top docs most relevant?
            context_recall,       # Did we find all needed info?
            context_relevancy,    # How much retrieved content is relevant?
            faithfulness,         # Is answer grounded in context?
            answer_relevancy      # Does answer address the question?
        ]
    
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
        
        # Run RAGAS evaluation
        result = evaluate(
            dataset,
            metrics=self.metrics,
            llm=os.getenv("GROQ_API_KEY"),  # Use Groq for LLM-as-judge
            embeddings=os.getenv("HF_TOKEN")  # HuggingFace embeddings
        )
        
        return {
            "context_precision": result["context_precision"],
            "context_recall": result["context_recall"],
            "context_relevancy": result["context_relevancy"],
            "faithfulness": result["faithfulness"],
            "answer_relevancy": result["answer_relevancy"],
            "overall_score": sum([
                result["context_precision"],
                result["context_recall"],
                result["context_relevancy"],
                result["faithfulness"],
                result["answer_relevancy"]
            ]) / 5
        }
    
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
    
    report += f"   Context Relevancy:  {interpretation['context_relevancy']['score']:.3f} "
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
