"""
Lightweight keyword-based intent classifier.
Replaces semantic-router which has heavy dependencies (litellm, numpy, etc.)
"""
from typing import Dict
import re

class SimpleIntentClassifier:
    """Keyword-based intent classification without ML dependencies"""
    
    def __init__(self):
        # Define keyword patterns for each intent
        self.intent_patterns = {
            "urgent": [
                r'\baudite?d?\b', r'\birs\b', r'\bpenalty\b', r'\bnotice\b',
                r'\bemergency\b', r'\burgent\b', r'\bdeadline\b', r'\btoday\b',
                r'\basap\b', r'\blocked\b'
            ],
            "complex_tax": [
                r'\bcapital gains?\b', r'\bcrypto\b', r'\bstaking\b',
                r'\bforeign tax\b', r'\b1031\b', r'\bexchange\b',
                r'\bqbi\b', r'\bqualified business income\b',
                r'\bmulti[- ]state\b', r'\binternational\b', r'\btreaty\b',
                r'\bk-?1\b', r'\bpartnership\b', r'\bdistribution\b'
            ],
            "bookkeeping": [
                r'\breconcil\w*\b', r'\bquickbooks\b', r'\bxero\b',
                r'\binvoice\b', r'\bpayroll\b', r'\bcash flow\b',
                r'\bchart of accounts\b', r'\bcategoriz\w*\b'
            ],
            "simple_tax": [
                r'\bstandard deduction\b', r'\bstd deduction\b',
                r'\bw-?2\b', r'\b1040\b', r'\bfiling\b', r'\brefund\b',
                r'\bdeduction\b', r'\btax bracket\b', r'\beitc\b',
                r'\bearned income\b', r'\bhome office\b', r'\bself[- ]employ\w*\b',
                r'\bextension\b'
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {
            intent: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for intent, patterns in self.intent_patterns.items()
        }
    
    def classify_intent(self, query: str) -> Dict:
        """Classify query into intent categories"""
        scores = {intent: 0 for intent in self.intent_patterns.keys()}
        scores["general"] = 0
        
        # Count matching keywords for each intent
        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(query):
                    scores[intent] += 1
        
        # Find best matching intent
        if max(scores.values()) == 0:
            return {
                "intent": "general",
                "confidence": 0.5
            }
        
        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        
        # Calculate confidence (normalize keyword matches)
        # More keywords = higher confidence, cap at 0.95
        confidence = min(0.95, 0.6 + (max_score * 0.15))
        
        return {
            "intent": best_intent,
            "confidence": confidence
        }

# Global instance
service_instance = None

def initialize():
    """Initialize the simple intent classifier"""
    global service_instance
    try:
        service_instance = SimpleIntentClassifier()
        print("✅ Simple intent classifier initialized")
    except Exception as e:
        print(f"⚠️ SimpleIntentClassifier initialization failed: {e}")
        service_instance = None
