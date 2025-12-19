"""
Query validation and disambiguation.
Prevents "garbage in, garbage out" by identifying ambiguous queries
and asking clarifying questions before hitting the RAG pipeline.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
import os
import logging

logger = logging.getLogger(__name__)

try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

class QueryValidator(BaseModel):
    """Structured output for query validation"""
    is_ambiguous: bool = Field(..., description="Whether the query lacks critical details")
    missing_info: List[str] = Field(default_factory=list, description="List of missing details (e.g., 'state', 'filing_status')")
    clarification_question: Optional[str] = Field(None, description="Question to ask user for clarification")
    confidence: float = Field(..., description="Confidence in this assessment 0.0-1.0")

async def validate_query(query: str) -> QueryValidator:
    """
    Validate if query has enough context for accurate retrieval.
    
    Args:
        query: User's tax question
        
    Returns:
        QueryValidator with disambiguation info
    """
    if not LITELLM_AVAILABLE:
        logger.warning("LiteLLM not available, skipping query validation")
        return QueryValidator(
            is_ambiguous=False,
            missing_info=[],
            confidence=0.5
        )
    
    try:
        prompt = f"""You are a tax expert assistant. Analyze this query for missing critical details.

Query: "{query}"

**PHILOSOPHY: Information First, Clarification Second**
- If the query asks a CLEAR question about a tax topic, mark as **NOT ambiguous** (is_ambiguous=false).
- The AI will provide a comprehensive answer covering all scenarios (e.g. all filing statuses) and THEN ask for details.
- Only mark as **ambiguous** if the query is a FRAGMENT with NO clear tax topic.

**EXAMPLES - NOT AMBIGUOUS (is_ambiguous=false)**:
- "What is the standard deduction?" -> Clear question. AI can provide all filing tax brackets.
- "What is the standard deduction for 2024?" -> Clear question.
- "Can I deduct my car?" -> Clear question. AI can explain self-employed vs employee rules.
- "When is the deadline?" -> Clear question.

**EXAMPLES - AMBIGUOUS (is_ambiguous=true)**:
- "What about home office?" -> Fragment. Unclear what they are asking.
- "Car deduction?" -> One word.
- "Can I deduct it?" -> Pronoun with no context.

Tax questions often require specific context (Filing status, State, Income type), BUT if the user asks a general question, let the AI answer generally FIRST.

Respond in JSON format:
{{
  "is_ambiguous": true/false,
  "missing_info": ["filing_status"],  // List missing details
  "clarification_question": "What is your filing status for 2024? (Single, Married Filing Jointly, Head of Household, etc.)",
  "confidence": 0.0-1.0
}}"""

        
        # Configurable Model
        model = os.getenv("QUERY_VALIDATOR_MODEL", "gpt-4o-mini")
        fallbacks_str = os.getenv("QUERY_VALIDATOR_FALLBACKS", "")
        fallbacks = [f.strip() for f in fallbacks_str.split(",")] if fallbacks_str else ["gemini/gemini-2.5-flash-lite-preview-09-2025"]

        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            fallbacks=fallbacks,
            timeout=5,
            max_tokens=200
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        return QueryValidator(**result)
        
    except Exception as e:
        logger.error(f"Query validation failed: {e}")
        # Fail open - don't block the pipeline
        return QueryValidator(
            is_ambiguous=False,
            missing_info=[],
            confidence=0.5
        )

# Global instance
service_instance = None

def initialize():
    """Initialize query validator"""
    global service_instance
    service_instance = True  # Stateless service
    logger.info("✅ Query validator initialized")
