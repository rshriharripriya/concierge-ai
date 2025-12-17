"""
Save evaluation results to Supabase instead of JSON files
"""
import os
import sys
from supabase import create_client
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def save_evaluation_to_supabase(results: dict):
    """
    Save evaluation results to Supabase evaluation_runs table
    
    Args:
        results: Dict from EvaluationRunner with metrics and test_results
    """
    
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("⚠️ Supabase credentials not found. Skipping database save.")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Extract metrics
    metrics = results.get("metrics", {})
    ragas = results.get("ragas_metrics", {})
    
    # Helper to convert percentage to decimal (80.0 -> 0.80)
    def to_decimal(value):
        if value is None:
            return None
        # If value > 1, assume it's a percentage
        if value > 1:
            return value / 100.0
        return value
    
    # Prepare row data (all metrics as 0.0-1.0 decimals)
    row = {
        "faithfulness": to_decimal(ragas.get("faithfulness")),
        "context_precision": to_decimal(ragas.get("context_precision")),
        "context_recall": to_decimal(ragas.get("context_recall")),
        "context_relevancy": to_decimal(ragas.get("context_relevancy")),
        "answer_relevancy": to_decimal(ragas.get("answer_relevancy")),
        
        "routing_accuracy": to_decimal(metrics.get("routing_accuracy")),
        "routing_accuracy_baseline": to_decimal(metrics.get("routing_accuracy_baseline")),
        "intent_accuracy": to_decimal(metrics.get("intent_accuracy")),
        "complexity_mae": metrics.get("complexity_mae"),
        "disambiguation_recall": to_decimal(metrics.get("disambiguation_recall")),
        
        "total_tests": metrics.get("total_tests"),
        "tests_passed": metrics.get("tests_passed"),
        "tests_failed": metrics.get("tests_failed"),
        
        "detailed_results": results,
        "evaluation_note": "Automated evaluation"
    }
    
    # Insert into database
    try:
        response = supabase.table("evaluation_runs").insert(row).execute()
        print(f"✅ Evaluation results saved to Supabase (ID: {response.data[0]['id']})")
        return response.data[0]
    except Exception as e:
        print(f"❌ Failed to save to Supabase: {e}")
        return None
