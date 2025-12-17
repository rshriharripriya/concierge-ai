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

Tax questions often require specific context:
- **Filing status**: Single, Married Filing Jointly, Married Filing Separately, Head of Household
- **State**: Tax rules vary by state
- **Income type**: W2 employee, self-employed, 1099 contractor, etc.
- **Tax year**: 2023, 2024, etc.
- **Amounts**: Specific dollar amounts for calculations

Guidelines:
- If query is SPECIFIC enough (e.g., "What's the 2024 standard deduction for single filers?"), mark as NOT ambiguous
- If query is TOO VAGUE (e.g., "Can I deduct my car?"), mark as ambiguous and ask a HELPFUL clarifying question
- Make clarification questions conversational and include common options in parentheses
- Examples of GOOD questions:
  - "What is your filing status for 2024? (Single, Married Filing Jointly, Head of Household, etc.)"
  - "Are you self-employed or a W2 employee?"
  - "Which state do you live in? (This affects state tax rules)"
- Don't be overly pedantic - only flag genuinely ambiguous queries

Respond in JSON format:
{{
  "is_ambiguous": true/false,
  "missing_info": ["filing_status"],  // List missing details
  "clarification_question": "What is your filing status for 2024? (Single, Married Filing Jointly, Head of Household, etc.)",  // Include options!
  "confidence": 0.0-1.0
}}"""

        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            fallbacks=["gemini/gemini-1.5-flash"],
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
