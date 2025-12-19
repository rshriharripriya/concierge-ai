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
    import litellm
    import logging
    # Aggressively silence LiteLLM
    litellm.set_verbose = False
    litellm.suppress_handler_errors = True
    litellm.add_status_to_exception = False
    litellm.telemetry = False
    logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
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
    routing_prompt = f"""You are a tax query classification system. Classify this query's intent and route.

Query: "{query}"

**PHILOSOPHY: Information First, Clarification Second**
- If the query asks a CLEAR question about a tax topic, route to AI (which will provide comprehensive answer + optional follow-up)
- Only route to clarification if the query is a FRAGMENT with no clear tax topic

**ALWAYS ROUTE TO AI (simple_tax):**
- "What is the standard deduction?" → AI provides all filing statuses, then asks user's status
- "What is the standard deduction for 2024?" → AI
- "When is the tax deadline?" → AI
- "Can I deduct my car?" → AI provides self-employed vs employee rules, then asks for details
- "What is a W-2?" → AI

**ONLY ROUTE TO CLARIFICATION (disambiguation_needed):**
- "What about home office?" → No clear question, just fragment
- "Car deduction?" → One-word, unclear what they're asking
- "That thing" → Pronoun-only reference

**INTENT CLASSIFICATION:**
1. **simple_tax** = Clear question about tax topic (provide info first)
2. **complex_tax** = Multi-state, crypto, trusts, estate, international  
3. **urgent** = IRS audit, penalty, deadline TODAY
4. **bookkeeping** = QuickBooks, Xero, accounting software
5. **disambiguation_needed** = Fragment with unclear topic

**ROUTING RULES:**
- simple_tax → route="ai" (RAG provides comprehensive answer + follow-up)
- complex_tax → route="human"
- urgent → route="human"
- bookkeeping → route="human"
- disambiguation_needed → route="clarification" (only for true fragments)

**COMPLEXITY (1-5):**
- 1 = Simple definition (W-2, standard deduction)
- 2 = Procedure (lost W-2, deadline extension)
- 3 = Scenario (home office, vehicle deduction)
- 4 = Multi-state, crypto, FBAR
- 5 = High-risk: audit, trust, ISO stock options, estate planning

**CRITICAL: Stock Options & Equity = Complex!**
- Any mention of ISO, RSU, stock options, equity → complex_tax, complexity=5

Respond ONLY with JSON:
{{
  "intent": "simple_tax" | "complex_tax" | "urgent" | "bookkeeping" | "disambiguation_needed",
  "route": "ai" | "human" | "clarification",
  "technical_complexity": 1-5,
  "urgency": 1-5,
  "risk_exposure": 1-5,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}"""

    try:
        
        # Provider Chain: Configurable via env
        model, fallbacks = get_model_config()
        
        logger.info(f"Attempting LLM routing with model: {model}")
        
        response = completion(
            model=model,
            messages=[{"role": "user", "content": routing_prompt}],
            response_format={"type": "json_object"},
            fallbacks=fallbacks,
            timeout=10,
            max_tokens=300
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Keep logs clean as requested by user, BUT print for debugging now
        print(f"❌ LLM Router Error (Model: {model}): {e}")
        logger.error(f"LLM routing failed with model {model}: {e}")
        raise



# Valid Intents
VALID_INTENTS = ["simple_tax", "complex_tax", "cryptocurrency", "small_business", "interaction"]

# Model Config
# Model Config
DEFAULT_MODEL = "gemini/gemini-2.0-flash-exp"
DEFAULT_FALLBACKS = ["groq/llama-3.1-8b-instant", "openrouter/google/gemini-1.5-flash"]

def get_model_config():
    """Get model and fallbacks from env"""
    model = os.getenv("LLM_ROUTER_MODEL", DEFAULT_MODEL)
    fallbacks_str = os.getenv("LLM_ROUTER_FALLBACKS", "")
    fallbacks = [f.strip() for f in fallbacks_str.split(",")] if fallbacks_str else DEFAULT_FALLBACKS
    return model, fallbacks

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
            if not result_json:
                raise ValueError("LLM returned empty response")
                
            result = json.loads(result_json)
            
            # Validate response structure
            required_fields = ['route', 'intent', 'technical_complexity', 'urgency', 'risk_exposure', 'confidence', 'reasoning']
            if not all(field in result for field in required_fields):
                # Fallback for old key name just in case
                if 'route_decision' in result:
                    result['route'] = result['route_decision']
                else:
                    raise ValueError(f"Missing required fields in LLM response: {result}")
            
            # Calculate overall complexity score (1-5)
            complexity_score = max(
                result.get('technical_complexity', 1),
                result.get('urgency', 1),
                result.get('risk_exposure', 1)
            )
            
            # Integrated intent from the unified LLM call (Saves 1 LLM call!)
            intent = result.get('intent', 'complex_tax')
            
            logger.info(f"LLM Unified decision: {result['route']} | Intent: {intent} (complexity: {complexity_score}, confidence: {result['confidence']:.2f})")
            
            return {
                "route": result['route'],
                "route_decision": result['route'], # For backward compatibility
                "router_type": "llm_unified",
                "intent": intent,
                "complexity_score": complexity_score,
                "confidence": result['confidence'],
                "reasoning": result['reasoning'],
                "method": "llm_unified",
                "complexity_breakdown": {
                    "technical": result.get('technical_complexity', 1),
                    "urgency": result.get('urgency', 1),
                    "risk": result.get('risk_exposure', 1)
                }
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
