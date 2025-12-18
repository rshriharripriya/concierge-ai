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
            "metrics": {},
            "efficiency": {
                "llm_calls_made": 0,
                "llm_calls_saved": 0
            }
        }
        # Service instances (injected in main)
        self.query_validator = None
        self.llm_router = None
        self.expert_matcher = None
        self.rag_service = None
        self.run_ragas = False # Default to False to save credits
    
    def load_golden_dataset(self, test_ids: List[str] = None) -> List[Dict]:
        """Load golden test dataset, optionally filtered by IDs"""
        # Handle both running from project root and evaluation directory
        # dataset_path = 'golden_dataset.json' if os.path.exists('golden_dataset.json') else 'evaluation/golden_dataset.json'
        dataset_path = 'golden_dataset.json'
        
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        all_cases = data['test_queries']
        if test_ids:
            return [tc for tc in all_cases if tc['id'] in test_ids]
        return all_cases
    
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
            self.results["efficiency"]["llm_calls_made"] += 1
            self.results["efficiency"]["llm_calls_saved"] += 1 # We saved the separate intent call
            
            result["actual"]["intent"] = routing_result.get("intent", "unknown")
            result["actual"]["complexity_score"] = routing_result.get("complexity_score", 0)
            # Router returns "route_decision" not "should_escalate"
            route_decision = routing_result.get("route", routing_result.get("route_decision", "ai"))
            result["actual"]["route_decision"] = route_decision
            
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
            
            # Step 4: RAG Answer Quality (if routed to AI OR clarification)
            # Ambiguous queries might be routed to 'clarification' but we still want to check the quality of prompt
            if result["actual"]["route_decision"] in ["ai", "clarification"]:
                # Access the service instance directly from the module to avoid NoneType issues
                from services import rag_service
                rag = rag_service.service_instance
                
                if rag:
                    rag_result = await rag.generate_answer(query, None)
                    self.results["efficiency"]["llm_calls_made"] += 1
                    
                    result["actual"]["answer"] = rag_result["answer"]
                    print(f"   Answer: {rag_result['answer']}") # PRINT ANSWER FOR USER VISIBILITY
                    
                    result["actual"]["contexts"] = rag_result["contexts"]
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
                        if contains_all:
                            print(f"   Answer Quality: PASS")
                        else:
                            print(f"   Answer Quality: FAIL")
                            print(f"      Got: '{rag_result['answer']}'")
                            print(f"      Missing keywords from: {test_case['expected_answer_contains']}")
                else:
                    result["error"] = "RAG service instance is None"
                    print(f"   ❌ ERROR: RAG service instance not initialized")
        
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ ERROR: {e}")
        
        return result
    
    async def run_all_tests(self, test_ids: List[str] = None):
        """Run all tests and calculate metrics"""
        test_cases = self.load_golden_dataset(test_ids)
        
        print(f"\n{'='*60}")
        print(f"CONCIERGE AI - EVALUATION RUN")
        if test_ids:
            print(f"RERUNNING {len(test_ids)} FAILED TESTS")
        print(f"{'='*60}")
        print(f"Total Test Cases: {len(test_cases)}\n")
        
        # Run all tests with delays to avoid rate limiting
        for i, test_case in enumerate(test_cases):
            result = await self.run_single_test(test_case)
            self.results["test_results"].append(result)
            
            # Add delay between requests to avoid rate limiting (except after last test)
            if i < len(test_cases) - 1:
                print(f"⏳ Sleeping 60s to avoid rate limits...")
                await asyncio.sleep(60)  # 60-second gap between tests
        
        # Step 5: Run RAGAS Evaluation (if requested)
        if self.run_ragas:
            await self.run_ragas_evaluation()
        else:
            print("\n⏭️ Skipping RAGAS evaluation (use --ragas to enable).")
        
        # Calculate metrics
        self.calculate_metrics()
        self.print_summary()
        self.save_results()

    async def run_ragas_evaluation(self):
        """Run RAGAS evaluation on AI-routed tests"""
        ai_results = [
            r for r in self.results["test_results"] 
            if r["actual"].get("route_decision") in ["ai", "clarification"] and "answer" in r["actual"]
        ]
        
        if not ai_results:
            print("\n⏭️ Skipping RAGAS: No AI responses recorded.")
            return

        print(f"\n🏆 Running RAGAS evaluation for {len(ai_results)} responses...")
        
        try:
            from evaluation.ragas_evaluator import RAGASEvaluator, format_ragas_report
            evaluator = RAGASEvaluator()
            
            # Prepare data
            ragas_data = []
            for r in ai_results:
                ragas_data.append({
                    "question": r["query"],
                    "answer": r["actual"]["answer"],
                    "contexts": r["actual"].get("contexts", []),
                    "ground_truth": r["expected"].get("ground_truth", "")
                })
            
            # Run evaluation
            scores = await evaluator.evaluate_rag_quality(ragas_data)
            interpretation = evaluator.interpret_scores(scores)
            
            # Save metrics
            self.results["ragas_metrics"] = scores
            
            # Print report
            print(format_ragas_report(scores, interpretation))
            
        except Exception as e:
            print(f"⚠️ RAGAS evaluation failed: {e}")
            self.results["ragas_metrics"] = {}

    def calculate_baseline_accuracy(self) -> float:
        """
        Calculate baseline routing accuracy using keyword-based SimpleIntentClassifier.
        This represents performance WITHOUT the LLM Router.
        """
        try:
            from services.semantic_router import SimpleIntentClassifier
            classifier = SimpleIntentClassifier()
            
            results = self.results["test_results"]
            correct_baseline = 0
            total_routable = 0
            
            for r in results:
                # Only check cases that have an expected route
                if "expected" not in r or "expected_route" not in r["expected"]:
                    continue
                
                total_routable += 1
                query = r["query"]
                expected_route = r["expected"]["expected_route"]
                
                # Run keyword classification
                intent_result = classifier.classify_intent(query)
                intent = intent_result["intent"]
                
                # Simple heuristic mapping for baseline router
                # This mimics the legacy routing logic before LLM
                if intent in ["urgent", "complex_tax", "bookkeeping"]:
                    baseline_route = "human"
                elif intent in ["simple_tax", "general"]:
                    baseline_route = "ai"
                else:
                    baseline_route = "ai" # Default
                    
                if baseline_route == expected_route:
                    correct_baseline += 1
            
            return (correct_baseline / total_routable * 100) if total_routable > 0 else 0.0
            
        except Exception as e:
            print(f"⚠️ Failed to calculate baseline accuracy: {e}")
            return 0.0

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
        
        # Expert matching accuracy
        expert_tests = [r for r in results if "expert_match" in r.get("passed", {})]
        expert_correct = sum(1 for r in expert_tests if r["passed"]["expert_match"])
        expert_accuracy = (expert_correct / len(expert_tests) * 100) if expert_tests else 0
        
        # Disambiguation recall (only for cases marked as disambiguation_needed)
        disambiguation_tests = [r for r in results if r["expected"].get("expected_intent") == "disambiguation_needed"]
        disambiguation_correct = sum(1 for r in disambiguation_tests if r["actual"].get("route_decision") == "clarification")
        disambiguation_recall = (disambiguation_correct / len(disambiguation_tests) * 100) if disambiguation_tests else 0
        
        self.results["metrics"] = {
            "routing_accuracy": round(routing_accuracy, 4),
            "intent_accuracy": round(intent_accuracy, 4),
            "complexity_mae": round(complexity_mae, 4),
            "disambiguation_recall": round(disambiguation_recall, 4),
            "expert_match_accuracy": round(expert_accuracy, 4),
            "efficiency_gain": f"{self.results['efficiency']['llm_calls_saved']} calls saved",
            "total_tests": len(results),
            "tests_passed": sum(1 for r in results if all(r.get("passed", {}).values())),
            "tests_failed": sum(1 for r in results if not all(r.get("passed", {}).values()) and r.get("passed")),
            "routing_accuracy_baseline": round(self.calculate_baseline_accuracy(), 4)
        }
        
        # Add RAGAS metrics only if they exist
        if "ragas_metrics" in self.results:
            self.results["metrics"]["ragas"] = self.results["ragas_metrics"]

    def print_summary(self):
        """Print evaluation summary"""
        metrics = self.results["metrics"]
        
        print(f"\n{'='*60}")
        print(f"EVALUATION RESULTS")
        print(f"{'='*60}\n")
        
        print(f"📊 METRICS:")
        print(f"   Routing Accuracy:        {metrics.get('routing_accuracy', 0):.2f}%")
        print(f"   Intent Accuracy:         {metrics.get('intent_accuracy', 0):.2f}%")
        print(f"   Complexity MAE:          {metrics.get('complexity_mae', 0):.2g}")
        print(f"   Disambiguation Recall:   {metrics.get('disambiguation_recall', 0):.2f}%")
        print(f"   Expert Match Accuracy:   {metrics.get('expert_match_accuracy', 0):.2f}%")
        
        print(f"\n⚡ EFFICIENCY:")
        print(f"   LLM Calls Made:          {self.results['efficiency']['llm_calls_made']}")
        print(f"   LLM Calls Saved:         {self.results['efficiency']['llm_calls_saved']} ✨")
        
        if "ragas" in metrics:
            print(f"\n🏆 RAGAS METRICS:")
            for metric_name, score in metrics["ragas"].items():
                if isinstance(score, (int, float)):
                    print(f"   {metric_name.replace('_', ' ').title()}: {score:.4f}")
                else:
                    print(f"   {metric_name.replace('_', ' ').title()}: {score}")
        
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
        """Save results to Supabase and clean up bulky data"""
        
        # Create a deep copy to modify for storage
        import copy
        storage_results = copy.deepcopy(self.results)
        
        # SLIM DOWN: Remove question/answer text from detailed_results to save space
        # We only keep IDs and pass/fail status
        for r in storage_results.get("test_results", []):
            # Remove bulky fields
            if "query" in r: del r["query"]
            if "expected" in r: del r["expected"]
            if "actual" in r:
                if "answer" in r["actual"]: del r["actual"]["answer"]
                if "contexts" in r["actual"]: del r["actual"]["contexts"]
            
        # Save to Supabase
        try:
            from evaluation.save_to_supabase import save_evaluation_to_supabase
            save_evaluation_to_supabase(storage_results)
        except Exception as e:
            print(f"❌ Could not save to Supabase: {e}")
            print("⚠️ Results not persisted - configure SUPABASE_URL and SUPABASE_KEY")
        
        print()


async def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Run Concierge AI Evaluation")
    parser.add_argument("--force", action="store_true", help="Bypass the one-week cooldown period")
    parser.add_argument("--rerun-failed", action="store_true", help="Only run tests that failed in the last run")
    parser.add_argument("--ragas", action="store_true", help="Run expensive RAGAS evaluation (off by default)")
    args = parser.parse_args()

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
    runner.run_ragas = args.ragas # Set RAGAS flag from CLI
    runner.query_validator = query_validator
    runner.llm_router = llm_router
    runner.expert_matcher = expert_matcher
    runner.rag_service = rag_service
    
    # Check failed tests if requested
    test_ids_to_run = None
    if args.rerun_failed:
        from evaluation.save_to_supabase import get_failed_test_ids
        test_ids_to_run = get_failed_test_ids()
        if not test_ids_to_run:
            print("✨ No failed tests found in the last run! Everything passed last time.")
            return
        print(f"🔍 Found {len(test_ids_to_run)} failed tests to rerun.")

    # Check if we should run the evaluation (only once a week)
    if not args.force:
        try:
            from evaluation.save_to_supabase import get_latest_evaluation_time
            from datetime import datetime, timedelta, timezone
            
            last_run = get_latest_evaluation_time()
            
            if last_run:
                # Ensure last_run is timezone-aware for comparison (Supabase returns UTC)
                if last_run.tzinfo is None:
                    last_run = last_run.replace(tzinfo=timezone.utc)
                    
                now = datetime.now(timezone.utc)
                one_week_ago = now - timedelta(weeks=1)
                
                if last_run > one_week_ago:
                    next_run_date = last_run + timedelta(weeks=1)
                    time_until = next_run_date - now
                    days = time_until.days
                    hours = int(time_until.seconds / 3600)
                    
                    print(f"\n⏳ Evaluation skipped: Last run was on {last_run.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    print(f"   Next run allowed in: {days} days, {hours} hours")
                    print(f"   (Scheduled for after: {next_run_date.strftime('%Y-%m-%d %H:%M:%S UTC')})")
                    print("   Use --force to run anyway.")
                    return
        except Exception as e:
            print(f"⚠️ Could not check last run time: {e}")
            print("   Continuing with evaluation...")

    await runner.run_all_tests(test_ids_to_run)


if __name__ == "__main__":
    asyncio.run(main())

