"""
Answer faithfulness scoring - ASYNC implementation.
Scores whether LLM answer is grounded in retrieved context.
Does NOT block user response.
"""
from typing import Dict
import os
import logging
import json

logger = logging.getLogger(__name__)

try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

async def score_faithfulness(query: str, answer: str, context_docs: list) -> Dict:
    """
    Score answer faithfulness using LLM-as-judge.
    This runs in the BACKGROUND and does not block user response.
    
    Args:
        query: Original user query
        answer: LLM-generated answer
        context_docs: Retrieved documents used
        
    Returns:
        Dict with faithfulness scores
    """
    if not LITELLM_AVAILABLE:
        logger.warning("LiteLLM not available, skipping faithfulness scoring")
        return {"faithfulness": 0.5, "method": "skipped"}
    
    try:
        # Build context string
        context = "\n\n".join([
            f"[Doc {i+1}]: {doc.get('content', '')[:200]}"
            for i, doc in enumerate(context_docs[:3])
        ])
        
        prompt = f"""Evaluate if this answer is grounded in the provided context.

Context:
{context}

Question: {query}
Answer: {answer}

Score from 0.0-1.0:
- 1.0 = Answer is fully supported by context
- 0.5 = Partially supported or unclear
- 0.0 = Answer contradicts or ignores context

Respond with ONLY a JSON object:
{{"faithfulness": 0.0-1.0, "reasoning": "brief explanation"}}"""

        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            fallbacks=["gemini/gemini-2.5-flash-preview-09-2025"],
            timeout=5,
            max_tokens=150
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.info(f"Faithfulness score: {result['faithfulness']:.2f} - {result['reasoning']}")
        return result
        
    except Exception as e:
        logger.error(f"Faithfulness scoring failed: {e}")
        return {"faithfulness": 0.5, "method": "error", "error": str(e)}

def calculate_confidence(
    retrieval_scores: Dict,
    answer_metadata: Dict,
    faithfulness_score: float = None
) -> float:
    """
    Calculate final confidence score from multiple signals.
    
    Args:
        retrieval_scores: {"max_similarity": float, "rerank_score": float}
        answer_metadata: {"has_citations": bool, "llm_confidence": float}
        faithfulness_score: Optional async score (may not be available yet)
        
    Returns:
        Combined confidence 0.0-1.0
    """
    # Retrieval quality (best doc similarity or rerank score)
    retrieval_quality = retrieval_scores.get('rerank_score') or retrieval_scores.get('max_similarity', 0.5)
    
    # Citation bonus
    citation_bonus = 0.05 if answer_metadata.get('has_citations') else 0.0
    
    if faithfulness_score is not None:
        # Full calculation with faithfulness (happens async)
        confidence = (
            faithfulness_score * 0.6 +
            retrieval_quality * 0.3 +
            answer_metadata.get('llm_confidence', 0.5) * 0.1 +
            citation_bonus
        )
    else:
        # Immediate calculation without faithfulness (for user response)
        confidence = (
            retrieval_quality * 0.7 +
            answer_metadata.get('llm_confidence', 0.5) * 0.3 +
            citation_bonus
        )
    
    return min(0.95, confidence)
