"""
LLM-as-judge routing using LiteLLM for provider fallback.
Replaces keyword-based routing with structured LLM decision-making.
"""
from typing import Dict, Optional
import os
import json
from functools import lru_cache
import logging
from services import llm_intent_classifier

logger = logging.getLogger(__name__)

try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning("LiteLLM not installed. Will use fallback keyword routing.")

@lru_cache(maxsize=100)
def cached_llm_routing(query: str) -> str:
    """
    Cached LLM routing decisions for common queries.
    Cache key is the query string.
    """
    return _get_llm_routing_decision(query)

def _get_llm_routing_decision(query: str) -> str:
    """
    Call LLM to make routing decision with structured JSON output.
    
    Returns JSON string with routing decision.
    """
    routing_prompt = f"""You are a tax question routing system. Analyze this query and provide a structured routing decision.

Query: "{query}"

Evaluate on these dimensions (1-5 scale):
- technical_complexity: How specialized is the tax knowledge needed? (1=basic, 5=expert-level)
- urgency: Does this require immediate attention? (1=no rush, 5=urgent deadline/audit)
- risk_exposure: What's the financial/legal risk of wrong advice? (1=low, 5=high penalties)

Routing rules:
- Route to "human" if: technical_complexity >= 4 OR urgency >= 4 OR risk_exposure >= 4
- Route to "ai" otherwise

Respond ONLY with valid JSON in this exact format:
{{
  "route_decision": "ai" or "human",
  "technical_complexity": 1-5,
  "urgency": 1-5,
  "risk_exposure": 1-5,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}"""

    try:
        # Groq → Gemini fallback chain (both free tier)
        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": routing_prompt}],
            response_format={"type": "json_object"},
            fallbacks=[
                "gemini/gemini-2.0-flash-exp"  # Google Gemini 2.0 Flash (experimental, free)
            ],
            timeout=10,
            max_tokens=300
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"LLM routing failed (both Groq and Gemini): {e}")
        raise

class LLMRouter:
    """LLM-as-judge routing with automatic provider fallback"""
    
    def __init__(self):
        self.enabled = LITELLM_AVAILABLE and os.getenv("USE_LLM_ROUTER", "true").lower() == "true"
        self.fallback_router = None
    
    def set_fallback_router(self, fallback_router):
        """Set keyword-based fallback router"""
        self.fallback_router = fallback_router
    
    async def route(self, query: str) -> Dict:
        """
        Route query using LLM-as-judge.
        
        Args:
            query: User query
            
        Returns:
            Dict with routing decision and metadata
        """
        if not self.enabled:
            logger.info("LLM router disabled, using fallback")
            return self._use_fallback(query)
        
        try:
            # Get cached LLM decision
            logger.info(f"Routing query with LLM: '{query[:50]}...'")
            result_json = cached_llm_routing(query)
            
            # Parse JSON response
            result = json.loads(result_json)
            
            # Validate response structure
            required_fields = ['route_decision', 'technical_complexity', 'urgency', 'risk_exposure', 'confidence', 'reasoning']
            if not all(field in result for field in required_fields):
                raise ValueError(f"Missing required fields in LLM response: {result}")
            
            # Calculate overall complexity score (1-5)
            complexity_score = max(
                result['technical_complexity'],
                result['urgency'],
                result['risk_exposure']
            )
            
            
            # Use LLM Intent Classifier for accurate intent detection
            intent_result = await llm_intent_classifier.service_instance.classify(query) if llm_intent_classifier.service_instance else {"intent": self._infer_intent(result), "confidence": 0.7}
            
            logger.info(f"LLM routing decision: {result['route_decision']} (complexity: {complexity_score}, confidence: {result['confidence']:.2f})")
            logger.info(f"Intent: {intent_result['intent']} (method: {intent_result.get('method', 'fallback')})")
            
            return {
                "route_decision": result['route_decision'],
                "complexity_score": complexity_score,
                "complexity_breakdown": {
                    "technical": result['technical_complexity'],
                    "urgency": result['urgency'],
                    "risk": result['risk_exposure']
                },
                "confidence": result['confidence'],
                "reasoning": result['reasoning'],
                "intent": intent_result['intent'],
                "intent_confidence": intent_result.get('confidence', 0.7),
                "router_type": "llm"
            }
            
        except Exception as e:
            logger.warning(f"LLM routing failed ({e}), using fallback keyword routing")
            return self._use_fallback(query)
    
    def _infer_intent(self, llm_result: Dict) -> str:
        """Infer intent category from LLM complexity scores"""
        if llm_result['urgency'] >= 4:
            return "urgent"
        elif llm_result['technical_complexity'] >= 4:
            return "complex_tax"
        elif llm_result['technical_complexity'] <= 2:
            return "simple_tax"
        else:
            return "general"
    
    def _use_fallback(self, query: str) -> Dict:
        """Use keyword-based fallback routing"""
        if self.fallback_router:
            logger.info("Using keyword fallback router")
            result = self.fallback_router.classify_intent(query)
            
            # Convert to LLM router format
            intent_complexity_map = {
                'simple_tax': 2,
                'complex_tax': 4,
                'urgent': 5,
                'bookkeeping': 3,
                'general': 2
            }
            
            complexity = intent_complexity_map.get(result['intent'], 3)
            route = "human" if complexity >= 4 else "ai"
            
            return {
                "route_decision": route,
                "complexity_score": complexity,
                "complexity_breakdown": {
                    "technical": complexity,
                    "urgency": 5 if result['intent'] == 'urgent' else 1,
                    "risk": complexity
                },
                "confidence": result['confidence'],
                "reasoning": f"Keyword-based classification: {result['intent']}",
                "intent": result['intent'],
                "router_type": "keyword_fallback"
            }
        else:
            # Ultimate fallback: route everything to AI
            logger.warning("No fallback router available, routing to AI by default")
            return {
                "route_decision": "ai",
                "complexity_score": 2,
                "complexity_breakdown": {"technical": 2, "urgency": 1, "risk": 2},
                "confidence": 0.5,
                "reasoning": "No routing available, defaulting to AI",
                "intent": "general",
                "router_type": "default"
            }

# Global instance
service_instance = None

def initialize(fallback_router=None):
    """Initialize LLM router with optional fallback"""
    global service_instance
    try:
        service_instance = LLMRouter()
        if fallback_router:
            service_instance.set_fallback_router(fallback_router)
        
        if service_instance.enabled:
            logger.info("✅ LLM router initialized with LiteLLM (Groq → Gemini fallback)")
        else:
            logger.info("⚠️ LLM router initialized but disabled, using keyword fallback only")
        return True
    except Exception as e:
        logger.error(f"⚠️ LLM router initialization failed: {e}")
        # Create fallback instance anyway - never leave it as None
        service_instance = LLMRouter()
        if fallback_router:
            service_instance.set_fallback_router(fallback_router)
        logger.info("✅ Created fallback LLM router instance")
        return False
