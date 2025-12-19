from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import sys

# Import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import llm_router as llm_router_lib
from services import rag_service as rag_service_lib
from services import expert_matcher as expert_matcher_lib
from services import query_validator

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
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Main query processing endpoint with async faithfulness scoring.
    1. LLM-based Routing
    2. RAG Response Generation  
    3. Expert Matching (if needed)
    4. Faithfulness Scoring (background - doesn't block response)
    """
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Normalize query for better handling of abbreviations
        normalized_query = request.query.replace(" std ", " standard ").replace("std ", "standard ")
        
        # STEP 0: Query Validation & Disambiguation
        # Prevent "garbage in, garbage out" by checking for ambiguity
        validation_result = await query_validator.validate_query(normalized_query)
        
        if validation_result.is_ambiguous and validation_result.confidence > 0.7:
            # Query is too vague - ask for clarification
            print(f"❓ Query ambiguous, asking for clarification: {validation_result.clarification_question}")
            
            # Return disambiguation response
            return QueryResponse(
                conversation_id=request.conversation_id or str(uuid.uuid4()),
                intent="disambiguation",
                complexity_score=0,
                route_decision="clarification_needed",
                response=validation_result.clarification_question,
                confidence=validation_result.confidence,
                expert=None,
                sources=[],
                reasoning=f"Missing: {', '.join(validation_result.missing_info)}"
            )
        
        # Get service instances
        llm_router = llm_router_lib.service_instance
        rag_service = rag_service_lib.service_instance
        expert_matcher = expert_matcher_lib.service_instance

        # Check if services are initialized
        if not llm_router or not rag_service or not expert_matcher:
            raise HTTPException(status_code=500, detail="Backend services failed to initialize. Please check server logs and environment variables (HF_TOKEN, SUPABASE_URL, COHERE_API_KEY, etc).")

        # Stage 1: LLM-based routing decision
        routing_result = await llm_router.route(request.query)
        intent = routing_result.get('intent', 'general')
        complexity_score = routing_result['complexity_score']
        route_decision = routing_result['route_decision']
        reasoning = routing_result['reasoning']
        
        print(f"🤖 LLM Router: {route_decision} (complexity: {complexity_score}/5, router: {routing_result['router_type']})")
        print(f"📍 Intent: {intent} | Breakdown: Tech={routing_result['complexity_breakdown']['technical']}, Urgency={routing_result['complexity_breakdown']['urgency']}, Risk={routing_result['complexity_breakdown']['risk']}")
        
        # Stage 2: Generate RAG response
        # Pass conversation_id for memory
        rag_result = await rag_service.generate_answer(
            request.query, 
            request.conversation_id
        )
        ai_confidence = rag_result['confidence']
        
        print(f"💡 AI Response generated (confidence: {ai_confidence})")
        
        # Stage 3: Final routing decision
        # LLM router already made primary decision, but we can override if AI confidence is very low
        urgency_detected = routing_result['complexity_breakdown']['urgency'] >= 4
        should_escalate = (route_decision == "human") or (ai_confidence < 0.60 and complexity_score >= 3)
        
        if should_escalate != (route_decision == "human"):
            print(f"🔄 Overriding LLM decision due to AI confidence: {ai_confidence}")
        
        # Stage 4: Expert matching (if escalating to human)
        expert = None
        if should_escalate:
            print(f"🔄 Escalating to expert (complexity: {complexity_score}, confidence: {ai_confidence}, urgency: {urgency_detected})")
            
            try:
                # Find best expert
                expert_result = await expert_matcher.find_best_expert(
                    request.query,
                    intent,
                    urgency_detected
                )
                
                if expert_result and 'expert' in expert_result:
                    expert = expert_result['expert']
                    # Add match_score to expert object for frontend display
                    expert['match_score'] = expert_result.get('match_score', 0)
                    print(f"✅ Matched expert: {expert.get('name', 'Unknown')} (score: {expert['match_score']:.2f})")
                else:
                    print("⚠️ No expert found, continuing with AI response")
                    should_escalate = False
            except Exception as e:
                print(f"❌ Expert matching failed: {e}, continuing with AI response")
                should_escalate = False
        
        print(f"✅ Final Route Decision: {'human' if should_escalate else 'ai'}")
        
        # Save messages to database
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Ensure conversation_id existsabase
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
            "assigned_expert_id": expert.get('id') if should_escalate and expert else None,
            "status": "escalated" if should_escalate else "active",
            "context": {
                "reasoning": reasoning,
                "urgency": urgency_detected,
                "router_type": routing_result['router_type'],
                "complexity_breakdown": routing_result['complexity_breakdown']
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
        
        # Format response based on routing decision
        if should_escalate and expert:
            response_content = f"I'll connect you with {expert.get('name', 'an expert')}, who specializes in {', '.join(expert.get('specialties', [])[:2])}. They'll be with you shortly."
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
        
        # ASYNC: Calculate faithfulness score in background (doesn't block user)
        if not should_escalate and rag_result.get('sources'):
            from services.faithfulness_scorer import score_faithfulness
            background_tasks.add_task(
                score_faithfulness,
                request.query,
                rag_result['answer'],
                rag_result['sources']
            )
        
        # Return response
        return QueryResponse(
            conversation_id=conversation_id,
            intent=intent,
            complexity_score=complexity_score,
            route_decision=route_decision,
            response=response_content,
            confidence=ai_confidence,
            expert=expert,
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
