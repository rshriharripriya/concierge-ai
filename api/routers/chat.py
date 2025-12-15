from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import sys

# Import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import semantic_router as semantic_router_lib
from services import complexity_scorer as complexity_scorer_lib
from services import rag_service as rag_service_lib
from services import expert_matcher as expert_matcher_lib

from supabase import create_client

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    user_id: str
    conversation_id: Optional[str] = None

class Source(BaseModel):
    title: str
    source: Optional[str] = None
    similarity: Optional[float] = None

class QueryResponse(BaseModel):
    conversation_id: str
    intent: str
    complexity_score: float
    route_decision: str
    response: str
    confidence: float
    expert: Optional[dict] = None
    sources: List[Source] = []
    reasoning: str

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main query processing endpoint implementing 4-stage routing:
    1. Intent Classification (Semantic Router)
    2. Complexity Scoring
    3. RAG Response Generation
    4. Expert Matching (if needed)
    """
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Normalize query for better handling of abbreviations
        normalized_query = request.query.replace(" std ", " standard ").replace("std ", "standard ")
        
        # Get service instances
        semantic_router = semantic_router_lib.service_instance
        complexity_scorer = complexity_scorer_lib.service_instance
        rag_service = rag_service_lib.service_instance
        expert_matcher = expert_matcher_lib.service_instance

        # Check if services are initialized
        if not semantic_router or not complexity_scorer or not rag_service or not expert_matcher:
            raise HTTPException(status_code=500, detail="Backend services failed to initialize. Please check server logs and environment variables (HF_TOKEN, SUPABASE_URL, etc).")

        # Stage 1: Classify intent
        intent_result = semantic_router.classify_intent(normalized_query)
        intent = intent_result.get('intent') or "general"
        
        print(f"📍 Intent: {intent} (confidence: {intent_result['confidence']})")
        
        # Stage 2: Score complexity
        complexity_result = complexity_scorer.score_complexity(request.query, intent)
        complexity_score = complexity_result['complexity_score']
        requires_expert = complexity_result['requires_expert']
        reasoning = complexity_result['reasoning']
        
        print(f"📊 Complexity: {complexity_score}/5 - {reasoning}")
        
        # Stage 3: Attempt RAG response
        # Pass conversation_id for memory
        rag_result = await rag_service.generate_answer(
            request.query, 
            request.conversation_id
        )
        ai_confidence = rag_result['confidence']
        
        print(f"🤖 AI Confidence: {ai_confidence}")
        
        # Stage 4: Routing decision
        # Confidence threshold determines when RAG confidence is high enough for AI response
        # Current: 0.60 - Consider lowering to 0.50-0.55 if knowledge base is comprehensive
        # Note: Improving knowledge base coverage is better than lowering threshold
        confidence_threshold = 0.60
        should_escalate = (
            requires_expert or 
            ai_confidence < confidence_threshold or
            complexity_score >= 4 or
            complexity_result['urgency_detected']
        )
        
        route_decision = "human" if should_escalate else "ai"
        expert_info = None
        
        print(f"🔀 Route Decision: {route_decision}")
        
        # If escalating, find best expert
        if should_escalate:
            expert_info = await expert_matcher.find_best_expert(
                request.query,
                intent,
                complexity_result['urgency_detected']
            )
            
            if expert_info:
                print(f"👤 Matched Expert: {expert_info['expert_name']} (score: {expert_info['match_score']})")
            else:
                print("⚠️ Expert matching failed or no expert found. Falling back to AI.")
                should_escalate = False
        
        # Create/update conversation in database
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        conversation_data = {
            "id": conversation_id,
            "user_id": request.user_id,
            "query": request.query,
            "intent": intent,
            "complexity_score": float(complexity_score),
            "route_decision": route_decision,
            "ai_response": rag_result['answer'],
            "ai_confidence": float(ai_confidence),
            "assigned_expert_id": expert_info['expert_id'] if should_escalate and expert_info else None,
            "status": "escalated" if should_escalate else "active",
            "context": {
                "reasoning": reasoning,
                "urgency": complexity_result['urgency_detected']
            }
        }
        
        supabase.table('conversations').upsert(conversation_data).execute()
        
        # Add user message to messages table
        user_message = {
            "conversation_id": conversation_id,
            "role": "user",
            "content": request.query,
            "metadata": {}
        }
        supabase.table('messages').insert(user_message).execute()
        
        # Add AI/expert response message
        if should_escalate and expert_info:
            response_content = f"I'll connect you with {expert_info['expert_name']}, who specializes in {', '.join(expert_info['specialties'][:2])}. {expert_info['expert_bio']} They'll be with you in {expert_info['estimated_wait']}."
        else:
            response_content = rag_result['answer']
        
        response_message = {
            "conversation_id": conversation_id,
            "role": "expert" if should_escalate else "assistant",
            "content": response_content,
            "metadata": {
                "confidence": ai_confidence,
                "sources": rag_result['sources']
            }
        }
        supabase.table('messages').insert(response_message).execute()
        
        # Return response
        return QueryResponse(
            conversation_id=conversation_id,
            intent=intent,
            complexity_score=complexity_score,
            route_decision=route_decision,
            response=response_content,
            confidence=ai_confidence,
            expert=expert_info,
            sources=rag_result['sources'],
            reasoning=reasoning
        )
        
    except Exception as e:
        print(f"❌ Error in process_query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Retrieve conversation history with messages"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Get conversation
        conv_result = supabase.table('conversations').select('*').eq('id', conversation_id).execute()
        
        if not conv_result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages
        messages_result = supabase.table('messages')\
            .select('*')\
            .eq('conversation_id', conversation_id)\
            .order('created_at')\
            .execute()
        
        return {
            "conversation": conv_result.data[0],
            "messages": messages_result.data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
