"""
Automated Evaluation Framework for Concierge AI
Provides reproducible metrics for routing accuracy, intent classification, and answer quality.
"""
import json
import asyncio
import sys
import os
from typing import Dict, List
from datetime import datetime

# Add parent directory to path BEFORE importing services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api'))





class EvaluationRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_results": [],
            "metrics": {}
        }
        # Service instances (injected in main)
        self.query_validator = None
        self.llm_router = None
        self.expert_matcher = None
        self.rag_service = None
    
    def load_golden_dataset(self) -> List[Dict]:
        """Load golden test dataset"""
        # Handle both running from project root and evaluation directory
        # dataset_path = 'golden_dataset.json' if os.path.exists('golden_dataset.json') else 'evaluation/golden_dataset.json'
        dataset_path = 'golden_dataset.json'
        
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        return data['test_queries']
    
    async def run_single_test(self, test_case: Dict) -> Dict:
        """Run a single test case through the pipeline"""
        query = test_case['query']
        test_id = test_case['id']
        
        print(f"\n🧪 Testing: {test_id}")
        print(f"   Query: {query}")
        
        result = {
            "test_id": test_id,
            "query": query,
            "expected": test_case,
            "actual": {},
            "passed": {}
        }
        
        try:
            # Skip query validation for now - focus on routing and RAG quality
            # The validator is optional and causing errors
            
            # Step 1: LLM Routing
            router = self.llm_router.service_instance
            if not router:
                result["error"] = "Router not initialized"
                return result
                
            
            routing_result = await router.route(query)
            
            result["actual"]["intent"] = routing_result.get("intent", "unknown")
            result["actual"]["complexity_score"] = routing_result.get("complexity_score", 0)
            # Router returns "route_decision" not "should_escalate"
            route_decision = routing_result.get("route_decision", "ai")
            result["actual"]["route_decision"] = "human" if route_decision == "human" else "ai"
            
            # Check intent
            if "expected_intent" in test_case:
                result["passed"]["intent"] = result["actual"]["intent"] == test_case["expected_intent"]
                print(f"   Intent: {result['actual']['intent']} (expected: {test_case['expected_intent']}) - {'PASS' if result['passed']['intent'] else 'FAIL'}")
            
            # Check routing
            if "expected_route" in test_case:
                result["passed"]["routing"] = result["actual"]["route_decision"] == test_case["expected_route"]
                print(f"   Route: {result['actual']['route_decision']} (expected: {test_case['expected_route']}) - {'PASS' if result['passed']['routing'] else 'FAIL'}")
            
            # Check complexity
            if "expected_complexity" in test_case:
                complexity_error = abs(result["actual"]["complexity_score"] - test_case["expected_complexity"])
                result["actual"]["complexity_error"] = complexity_error
                result["passed"]["complexity"] = complexity_error <= 1  # Allow ±1 error
                print(f"   Complexity: {result['actual']['complexity_score']} (expected: {test_case['expected_complexity']}) - {'PASS' if result['passed']['complexity'] else 'FAIL'}")
            
            # Step 3: Expert Matching (if routed to human)
            if result["actual"]["route_decision"] == "human":
                matcher = self.expert_matcher.service_instance
                expert_result = await matcher.find_best_expert(
                    query,
                    result["actual"]["intent"],
                    test_case.get("urgency", False)
                )
                
                if expert_result and 'expert' in expert_result:
                    result["actual"]["matched_expert"] = expert_result['expert']['name']
                    result["actual"]["expert_specialties"] = expert_result['expert']['specialties']
                    result["actual"]["match_score"] = expert_result['match_score']
                    
                    # Check if specialty matches
                    if "expected_expert_specialty" in test_case:
                        specialty_match = any(
                            test_case["expected_expert_specialty"] in spec 
                            for spec in expert_result['expert']['specialties']
                        )
                        result["passed"]["expert_match"] = specialty_match
                        print(f"   Expert: {expert_result['expert']['name']} - {'PASS' if specialty_match else 'FAIL'}")
            
            # Step 4: RAG Answer Quality (if routed to AI)
            if result["actual"]["route_decision"] == "ai":
                rag = self.rag_service.service_instance
                rag_result = await rag.generate_answer(query, None)
                
                result["actual"]["answer"] = rag_result["answer"]
                result["actual"]["confidence"] = rag_result["confidence"]
                result["actual"]["num_sources"] = len(rag_result["sources"])
                
                # Check if answer contains expected keywords
                if "expected_answer_contains" in test_case:
                    answer_lower = rag_result["answer"].lower()
                    contains_all = all(
                        keyword.lower() in answer_lower 
                        for keyword in test_case["expected_answer_contains"]
                    )
                    result["passed"]["answer_quality"] = contains_all
                    print(f"   Answer Quality: {'PASS' if contains_all else 'FAIL'}")
        
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ ERROR: {e}")
        
        return result
    
    async def run_all_tests(self):
        """Run all tests and calculate metrics"""
        test_cases = self.load_golden_dataset()
        
        print(f"\n{'='*60}")
        print(f"CONCIERGE AI - EVALUATION RUN")
        print(f"{'='*60}")
        print(f"Total Test Cases: {len(test_cases)}\n")
        
        # Run all tests
        for test_case in test_cases:
            result = await self.run_single_test(test_case)
            self.results["test_results"].append(result)
        
        # Calculate metrics
        self.calculate_metrics()
        self.print_summary()
        self.save_results()
    
    def calculate_metrics(self):
        """Calculate aggregate metrics"""
        results = self.results["test_results"]
        
        # Routing accuracy
        routing_tests = [r for r in results if "routing" in r.get("passed", {})]
        routing_correct = sum(1 for r in routing_tests if r["passed"]["routing"])
        routing_accuracy = (routing_correct / len(routing_tests) * 100) if routing_tests else 0
        
        # Intent accuracy
        intent_tests = [r for r in results if "intent" in r.get("passed", {})]
        intent_correct = sum(1 for r in intent_tests if r["passed"]["intent"])
        intent_accuracy = (intent_correct / len(intent_tests) * 100) if intent_tests else 0
        
        # Complexity MAE
        complexity_errors = [r["actual"].get("complexity_error", 0) for r in results if "complexity_error" in r.get("actual", {})]
        complexity_mae = sum(complexity_errors) / len(complexity_errors) if complexity_errors else 0
        
        # Disambiguation recall
        disambiguation_tests = [r for r in results if "disambiguation" in r.get("passed", {})]
        disambiguation_correct = sum(1 for r in disambiguation_tests if r["passed"]["disambiguation"])
        disambiguation_recall = (disambiguation_correct / len(disambiguation_tests) * 100) if disambiguation_tests else 0
        
        # Expert matching accuracy
        expert_tests = [r for r in results if "expert_match" in r.get("passed", {})]
        expert_correct = sum(1 for r in expert_tests if r["passed"]["expert_match"])
        expert_accuracy = (expert_correct / len(expert_tests) * 100) if expert_tests else 0
        
        self.results["metrics"] = {
            "routing_accuracy": round(routing_accuracy, 2),
            "intent_accuracy": round(intent_accuracy, 2),
            "complexity_mae": round(complexity_mae, 2),
            "disambiguation_recall": round(disambiguation_recall, 2),
            "expert_match_accuracy": round(expert_accuracy, 2),
            "total_tests": len(results),
            "tests_passed": sum(1 for r in results if all(r.get("passed", {}).values())),
            "tests_failed": sum(1 for r in results if not all(r.get("passed", {}).values()) and r.get("passed"))
        }
    
    def print_summary(self):
        """Print evaluation summary"""
        metrics = self.results["metrics"]
        
        print(f"\n{'='*60}")
        print(f"EVALUATION RESULTS")
        print(f"{'='*60}\n")
        
        print(f"📊 METRICS:")
        print(f"   Routing Accuracy:        {metrics['routing_accuracy']}%")
        print(f"   Intent Accuracy:         {metrics['intent_accuracy']}%")
        print(f"   Complexity MAE:          {metrics['complexity_mae']}")
        print(f"   Disambiguation Recall:   {metrics['disambiguation_recall']}%")
        print(f"   Expert Match Accuracy:   {metrics['expert_match_accuracy']}%")
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Tests:    {metrics['total_tests']}")
        print(f"   Passed:         {metrics['tests_passed']} ✅")
        print(f"   Failed:         {metrics['tests_failed']} ❌")
        
        # Rating
        avg_accuracy = (metrics['routing_accuracy'] + metrics['intent_accuracy']) / 2
        if avg_accuracy >= 90:
            rating = "🌟 EXPERT LEVEL (9-10/10)"
        elif avg_accuracy >= 80:
            rating = "✨ STRONG (7-8/10)"
        elif avg_accuracy >= 70:
            rating = "👍 GOOD (6-7/10)"
        else:
            rating = "⚠️  NEEDS IMPROVEMENT (<6/10)"

        
        print(f"\n🎯 OVERALL RATING: {rating}")
        print(f"{'='*60}\n")
    
    def save_results(self):
        """Save results to Supabase only (no JSON files)"""
        
        # Save to Supabase
        try:
            from evaluation.save_to_supabase import save_evaluation_to_supabase
            result = save_evaluation_to_supabase(self.results)
            if result:
                print(f"✅ Evaluation results saved to Supabase (ID: {result['id']})")
            else:
                print("⚠️ Failed to save to Supabase")
        except Exception as e:
            print(f"❌ Could not save to Supabase: {e}")
            print("⚠️ Results not persisted - configure SUPABASE_URL and SUPABASE_KEY")
        
        print()


async def main():
    """Main entry point"""
    # Load environment variables from .env.local
    from dotenv import load_dotenv
    import os
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env.local')
    load_dotenv(dotenv_path=env_path)
    print(f"🔑 Loaded env from: {env_path}")
    
    # Import services after path is set up
    from services import query_validator, llm_router, expert_matcher, rag_service
    from services import initialize_all
    
    # Initialize services
    print("🚀 Initializing services...")
    initialize_all()
    
    # Run evaluation
    runner = EvaluationRunner()
    runner.query_validator = query_validator
    runner.llm_router = llm_router
    runner.expert_matcher = expert_matcher
    runner.rag_service = rag_service
    
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

