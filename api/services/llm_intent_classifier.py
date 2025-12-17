"""
LLM-Based Intent Classifier - Replaces Keyword Regex Approach
Uses the LLM to classify intent with few-shot prompting for accuracy.
"""
import os
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from functools import lru_cache


@lru_cache(maxsize=1)
def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1  # Low temperature for classification
    )


class LLMIntentClassifier:
    """
    Use LLM for intent classification with few-shot examples.
    More accurate than regex, adapts to varied phrasings.
    """
    
    def __init__(self):
        self.llm = get_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert tax query classifier. Classify the user's query into ONE of these intents:

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

**CRITICAL RULES:**
1. Output ONLY the intent name, nothing else
2. Do not explain your reasoning in the output
3. When in doubt between simple and complex, choose complex
4. Urgent overrides everything if there's time pressure
5. Missing context = disambiguation_needed

Query: {query}
Intent:"""),
        ])
    
    async def classify(self, query: str) -> Dict[str, any]:
        """
        Classify query intent using LLM.
        
        Returns:
            {
                "intent": str,
                "confidence": float,
                "method": "llm"
            }
        """
        try:
            chain = self.prompt | self.llm
            response = await chain.ainvoke({"query": query})
            
            intent_text = response.content.strip().lower()
            
            # Parse LLM response (should be just the intent name)
            valid_intents = ["simple_tax", "complex_tax", "urgent", "bookkeeping", "disambiguation_needed"]
            
            # Extract intent from response
            intent = next((i for i in valid_intents if i in intent_text), "complex_tax")
            
            # LLM classifications are generally high confidence
            confidence = 0.9 if intent in intent_text else 0.7
            
            return {
                "intent": intent,
                "confidence": confidence,
                "method": "llm",
                "raw_response": response.content
            }
        
        except Exception as e:
            print(f"⚠️ LLM intent classification failed: {e}")
            # Fallback to conservative default
            return {
                "intent": "complex_tax",
                "confidence": 0.5,
                "method": "error_fallback",
                "error": str(e)
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
