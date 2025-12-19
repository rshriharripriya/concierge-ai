from typing import Dict

try:
    from litellm import completion
    import litellm
    import logging
    # Aggressively silence LiteLLM
    litellm.set_verbose = False
    litellm.suppress_handler_errors = True
    litellm.add_status_to_exception = False
    logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class LLMIntentClassifier:
    """
    Use LLM for intent classification with few-shot examples.
    Uses LiteLLM for automatic provider fallback.
    """
    
    def __init__(self):
        self.enabled = LITELLM_AVAILABLE
        # Raw system prompt template
        self.system_prompt_template = """You are an expert tax query classifier. Classify the user's query into ONE of these intents:

**INTENT DEFINITIONS:**
- simple_tax: Straightforward tax questions with clear answers (forms, deadlines, definitions)
- complex_tax: Multi-faceted tax scenarios requiring professional judgment (capital gains, multi-state, business structures)
- urgent: Time-sensitive issues requiring immediate expert attention (audits, penalties, deadlines)
- bookkeeping: Accounting/bookkeeping questions (QuickBooks, categorization, reconciliation)
- disambiguation_needed: Vague question missing critical context

**FEW-SHOT EXAMPLES:**

Query: "What is the standard deduction for 2024?"
Intent: simple_tax
Reasoning: Clear factual question with straightforward answer

Query: "I sold cryptocurrency and also have staking rewards from multiple wallets. How do I report this?"
Intent: complex_tax
Reasoning: Multiple tax implications, requires detailed analysis

Query: "I received an IRS audit notice yesterday"
Intent: urgent
Reasoning: Time-sensitive, requires immediate professional help

Query: "How do I categorize meals in QuickBooks?"
Intent: bookkeeping
Reasoning: Accounting software question

Query: "Can I deduct my car?"
Intent: disambiguation_needed
Reasoning: Missing context (self-employed? commute? business use?)

Query: "As a US citizen living abroad, do I need to file FBAR?"
Intent: complex_tax
Reasoning: International tax compliance with potential penalties, requires specific expertise

**CRITICAL RULES:**
1. Output ONLY the intent name, nothing else
2. Do not explain your reasoning in the output
3. When in doubt between simple and complex, choose complex
4. International tax queries (FBAR, FATCA, foreign income) are ALWAYS complex_tax
5. Urgent overrides everything if there's time pressure
6. Missing context = disambiguation_needed

Query: {query}
Intent:"""
    
    async def classify(self, query: str) -> Dict[str, any]:
        """Classify query intent using LLM with fallback"""
        if not self.enabled:
            return {"intent": "complex_tax", "confidence": 0.5, "method": "fallback_disabled"}

        try:
            # Format prompt manually since we are using completion()
            formatted_prompt = self.system_prompt_template.format(query=query)
            
            # Configurable Model
            model = os.getenv("INTENT_CLASSIFIER_MODEL", "gpt-4o-mini")
            fallbacks_str = os.getenv("INTENT_CLASSIFIER_FALLBACKS", "")
            fallbacks = [f.strip() for f in fallbacks_str.split(",")] if fallbacks_str else ["gemini/gemini-2.5-flash-lite-preview-09-2025"]

            # Provider Chain: Configurable via env
            response = completion(
                model=model,
                messages=[{"role": "user", "content": formatted_prompt}],
                fallbacks=fallbacks,
                temperature=0.1,
                timeout=10,
                max_tokens=50
            )
            
            intent_text = response.choices[0].message.content.strip().lower()
            
            # Extract valid intent
            valid_intents = ["simple_tax", "complex_tax", "urgent", "bookkeeping", "disambiguation_needed"]
            intent = next((i for i in valid_intents if i in intent_text), "complex_tax")
            
            # LLM classifications are generally high confidence
            confidence = 0.9 if intent in intent_text else 0.7
            
            return {
                "intent": intent,
                "confidence": confidence,
                "method": "llm",
                "raw_response": response.choices[0].message.content
            }
        
        except Exception:
            # Clean logging as requested
            print("⚠️ Intent classification failed: All providers exhausted. Using fallback.")
            return {
                "intent": "complex_tax",
                "confidence": 0.5,
                "method": "error_fallback"
            }


# Global instance
service_instance = None

def initialize():
    """Initialize the LLM intent classifier"""
    global service_instance
    try:
        service_instance = LLMIntentClassifier()
        print("✅ LLM Intent Classifier ready")
    except Exception as e:
        print(f"⚠️ LLM Intent Classifier initialization failed: {e}")
        service_instance = None
