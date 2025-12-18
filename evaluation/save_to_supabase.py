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
        "context_relevancy": to_decimal(ragas.get("context_relevance") or ragas.get("context_relevancy")),
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

def get_latest_evaluation_time():
    """
    Fetch the timestamp of the latest evaluation run from Supabase
    
    Returns:
        datetime object of the last run, or None if no runs exist
    """
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("⚠️ Supabase credentials not found. Cannot fetch latest run.")
        return None
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Get the most recent run ordered by created_at desc, limit 1
        response = supabase.table("evaluation_runs") \
            .select("created_at") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
            
        if response.data and len(response.data) > 0:
            # Parse timestamp string to datetime object
            timestamp_str = response.data[0]["created_at"]
            # Supabase usually returns ISO 8601 strings
            # Handle potential 'Z' for UTC or other formats
            try:
                if timestamp_str.endswith('Z'):
                    timestamp_str = timestamp_str.replace('Z', '+00:00')
                return datetime.fromisoformat(timestamp_str)
            except ValueError:
                print(f"⚠️ Could not parse timestamp: {timestamp_str}")
                return None
        return None
        
    except Exception as e:
        print(f"⚠️ Failed to fetch latest run: {e}")
        return None

def get_failed_test_ids():
    """
    Fetch the IDs of tests that failed in the most recent evaluation run
    
    Returns:
        List of test_id strings that failed, or empty list
    """
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        return []
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Get the most recent run's detailed_results
        response = supabase.table("evaluation_runs") \
            .select("detailed_results") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
            
        if response.data and len(response.data) > 0:
            detailed = response.data[0].get("detailed_results", {})
            test_results = detailed.get("test_results", [])
            
            failed_ids = []
            for result in test_results:
                # A test is considered failed if it has any failures in its 'passed' dict
                # or if it has an 'error' field
                passed_vals = result.get("passed", {}).values()
                if not all(passed_vals) or result.get("error"):
                    failed_ids.append(result.get("test_id"))
            
            return failed_ids
        return []
        
    except Exception as e:
        print(f"⚠️ Failed to fetch failed test IDs: {e}")
        return []
