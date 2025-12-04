from typing import Dict
import re

class ComplexityScorer:
    """
    Heuristic-based complexity scorer optimized for serverless (no LLM call).
    Scores from 1-5 based on keyword analysis and query patterns.
    """
    
    def __init__(self):
        # Keyword categories for scoring
        self.urgency_keywords = [
            'urgent', 'asap', 'deadline', 'today', 'audit', 'notice', 
            'penalty', 'emergency', 'immediately', 'now'
        ]
        
        self.complex_keywords = [
            'international', 'foreign', 'crypto', 'cryptocurrency', 'capital gains',
            'partnership', 'trust', 'estate', 'alternative minimum tax', 'amt',
            'section 1031', 'like-kind exchange', 'qualified business income', 'qbi',
            'passive activity loss', 'net operating loss', 'multi-state'
        ]
        
        self.moderate_keywords = [
            'self-employed', 'schedule c', 'depreciation', 'business expenses',
            'home office', 'rental income', 'investment', 'stock', 'dividend'
        ]
        
        self.simple_keywords = [
            'standard deduction', 'filing status', 'w-2', 'refund', 'deadline',
            'extension', 'tax bracket', 'irs', 'form 1040'
        ]
    
    def score_complexity(self, query: str, intent: str) -> Dict:
        """
        Score query complexity from 1-5
        1 = Simple factual question
        2 = Straightforward application
        3 = Moderate complexity
        4 = Complex specialized
        5 = Expert-level
        """
        query_lower = query.lower()
        
        # Check urgency
        has_urgency = any(keyword in query_lower for keyword in self.urgency_keywords)
        
        # Check complexity indicators
        complex_count = sum(1 for kw in self.complex_keywords if kw in query_lower)
        moderate_count = sum(1 for kw in self.moderate_keywords if kw in query_lower)
        simple_count = sum(1 for kw in self.simple_keywords if kw in query_lower)
        
        # Query length analysis
        word_count = len(query.split())
        has_numbers = bool(re.search(r'\d+', query))
        has_multiple_questions = query.count('?') > 1
        
        # Base score on intent
        intent_scores = {
            'simple_tax': 2,
            'complex_tax': 4,
            'bookkeeping': 3,
            'urgent': 5,
            'general': 2
        }
        
        base_score = intent_scores.get(intent, 3)
        
        # Adjust based on keywords
        if complex_count > 0:
            base_score = max(base_score, 4)
        elif moderate_count > 0:
            base_score = max(base_score, 3)
        elif simple_count > 0:
            base_score = min(base_score, 2)
        
        # Adjust for query characteristics
        if word_count > 30:
            base_score = min(5, base_score + 1)
        
        if has_multiple_questions:
            base_score = min(5, base_score + 1)
        
        # Urgency always escalates
        if has_urgency:
            base_score = 5
        
        # Clamp between 1-5
        final_score = max(1, min(5, base_score))
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            final_score, 
            has_urgency, 
            complex_count, 
            moderate_count,
            intent
        )
        
        return {
            "complexity_score": final_score,
            "reasoning": reasoning,
            "requires_expert": final_score >= 4 or has_urgency,
            "urgency_detected": has_urgency
        }
    
    def _generate_reasoning(self, score: int, urgency: bool, 
                           complex: int, moderate: int, intent: str) -> str:
        if urgency:
            return "Urgent situation detected - immediate expert assignment required"
        
        if score >= 4:
            if complex > 0:
                return f"Complex tax scenario identified ({intent}) - expert knowledge required"
            return "High complexity query requiring specialized expertise"
        
        if score == 3:
            return f"Moderate complexity ({intent}) - AI can assist with expert backup"
        
        return "Straightforward question suitable for AI response"

# Global instance
service_instance = None

def initialize():
    """Initialize the ComplexityScorer service"""
    global service_instance
    try:
        service_instance = ComplexityScorer()
        print("✅ ComplexityScorer service ready")
    except Exception as e:
        print(f"⚠️ ComplexityScorer initialization failed: {e}")
        service_instance = None

