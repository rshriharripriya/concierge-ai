"""
API endpoint to serve latest evaluation metrics.
Reads the most recent evaluation results JSON file.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
import os
import json
from datetime import datetime
from pathlib import Path

router = APIRouter()

@router.get("/latest")
async def get_latest_metrics() -> Dict:
    """
    Get the latest evaluation metrics from Supabase.
    
    Returns:
        {
            "timestamp": "2024-12-16T21:00:00",
            "ragas_metrics": {...},
            "routing_metrics": {...},
            ...
        }
    """
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise HTTPException(status_code=500, detail="Supabase credentials not configured")
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Fetch latest evaluation run
        response = supabase.table("evaluation_runs")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if not response.data or len(response.data) == 0:
            # Return placeholder if no data
            return {
                "timestamp": datetime.now().isoformat(),
                "ragas_metrics": {
                    "faithfulness": 0.0,
                    "context_precision": 0.0,
                    "context_recall": 0.0,
                    "context_relevancy": 0.0,
                    "answer_relevancy": 0.0
                },
                "routing_metrics": {
                    "baseline": 0.0,
                    "llm_based": 0.0,
                    "improvement_percentage": None
                },
                "total_tests": 0,
                "note": "No evaluation results available yet. Run evaluation to generate metrics."
            }
        
        latest = response.data[0]
        
        # Calculate staleness
        created_at = datetime.fromisoformat(latest['created_at'].replace('Z', '+00:00'))
        file_age_hours = (datetime.now(created_at.tzinfo) - created_at).total_seconds() / 3600
        is_stale = file_age_hours > 24
        
        # Calculate routing accuracy improvement
        baseline_acc = float(latest['routing_accuracy_baseline']) if latest['routing_accuracy_baseline'] else 0.0
        llm_acc = float(latest['routing_accuracy']) if latest['routing_accuracy'] else 0.0
        
        # Calculate percentage point improvement
        improvement_percentage = None
        if baseline_acc > 0:
            improvement_percentage = round((llm_acc - baseline_acc) * 100, 1)
        
        # Format response
        return {
            "timestamp": latest['created_at'],
            "ragas_metrics": {
                "faithfulness": float(latest['faithfulness']) if latest['faithfulness'] else 0.0,
                "context_precision": float(latest['context_precision']) if latest['context_precision'] else 0.0,
                "context_recall": float(latest['context_recall']) if latest['context_recall'] else 0.0,
                "context_relevancy": float(latest['context_relevancy']) if latest['context_relevancy'] else 0.0,
                "answer_relevancy": float(latest['answer_relevancy']) if latest['answer_relevancy'] else 0.0
            },
            "routing_metrics": {
                "baseline": baseline_acc,
                "llm_based": llm_acc,
                "improvement_percentage": improvement_percentage
            },
            "intent_accuracy": float(latest['intent_accuracy']) if latest['intent_accuracy'] else 0.0,
            "total_tests": latest['total_tests'] or 0,
            "tests_passed": latest['tests_passed'] or 0,
            "tests_failed": latest['tests_failed'] or 0,
            "file_age_hours": round(file_age_hours, 1),
            "is_stale": is_stale,
            "staleness_warning": f"⚠️ Results are {round(file_age_hours, 1)} hours old. Re-run evaluation to update." if is_stale else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching evaluation results: {str(e)}")
