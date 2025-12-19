from fastapi import APIRouter, HTTPException
from supabase import create_client
import os

router = APIRouter()

@router.get("/available")
async def get_available_experts():
    """Get all available experts with their profiles"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        result = supabase.table('experts')\
            .select('id, name, bio, avatar_url, specialties, performance_metrics, availability')\
            .execute()
        
        # Count available experts
        available_count = sum(
            1 for expert in result.data 
            if expert.get('availability', {}).get('status') == 'available'
        )
        
        return {
            "experts": result.data,
            "total": len(result.data),
            "available": available_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{expert_id}")
async def get_expert_details(expert_id: str):
    """Get detailed profile for a specific expert"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        result = supabase.table('experts').select('*').eq('id', expert_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Expert not found")
        
        expert = result.data[0]
        
        # Get recent interactions count
        interactions = supabase.table('conversations')\
            .select('id')\
            .eq('assigned_expert_id', expert_id)\
            .limit(10)\
            .execute()
        
        expert['recent_interactions'] = len(interactions.data) if interactions.data else 0
        
        return expert
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
