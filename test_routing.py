#!/usr/bin/env python3
"""
Quick test script to verify routing improvements
Run after knowledge base documents are added
"""
import requests
import json

API_URL = "http://localhost:8000/api/chat/query"

test_queries = [
    {
        "name": "Standard Deduction",
        "query": "What is the standard deduction?",
        "expected_intent": "simple_tax",
        "expected_complexity": 2,
        "expected_route": "ai",
        "expected_confidence": 0.70,
    },
    {
        "name": "Informal Phrasing",
        "query": "tell me all you know about std deduction",
        "expected_intent": "simple_tax",
        "expected_complexity": 2,
        "expected_route": "ai",
        "expected_confidence": 0.65,
    },
    {
        "name": "Home Office",
        "query": "Can I deduct my home office expenses?",
        "expected_intent": "simple_tax",
        "expected_complexity": 2,
        "expected_route": "ai",
        "expected_confidence": 0.60,
    },
    {
        "name": "F-1 Student (baseline)",
        "query": "as an f1 student, do i have to pay taxes?",
        "expected_intent": "simple_tax",
        "expected_complexity": 2,
        "expected_route": "ai",
        "expected_confidence": 0.75,
    },
]

def test_query(test_case):
    """Test a single query"""
    print(f"\n{'='*60}")
    print(f"Test: {test_case['name']}")
    print(f"Query: \"{test_case['query']}\"")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            API_URL,
            json={"query": test_case["query"], "user_id": "test_user"}
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        
        # Print results
        print(f"\n📊 Results:")
        print(f"  Intent:       {data['intent']} (expected: {test_case['expected_intent']})")
        print(f"  Complexity:   {data['complexity_score']} (expected: ≤{test_case['expected_complexity']})")
        print(f"  Route:        {data['route_decision']} (expected: {test_case['expected_route']})")
        print(f"  Confidence:   {data['confidence']:.2f} (expected: ≥{test_case['expected_confidence']})")
        print(f"  Reasoning:    {data['reasoning']}")
        
        # Check expectations
        passed = True
        
        if data['intent'] != test_case['expected_intent']:
            print(f"\n⚠️  Intent mismatch!")
            passed = False
        
        if data['complexity_score'] > test_case['expected_complexity']:
            print(f"\n⚠️  Complexity too high!")
            passed = False
        
        if data['route_decision'] != test_case['expected_route']:
            print(f"\n❌ Routing FAILED - still escalating to human!")
            passed = False
        
        if data['confidence'] < test_case['expected_confidence']:
            print(f"\n⚠️  Confidence below target (knowledge base may need improvement)")
            passed = False
        
        if passed:
            print("\n✅ PASSED")
        
        return passed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 Testing Routing System Improvements")
    print("="*60)
    
    results = []
    for test_case in test_queries:
        results.append((test_case['name'], test_query(test_case)))
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📈 SUMMARY")
    print(f"{'='*60}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed_count}/{total_count} passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Routing improvements are working.")
    else:
        print("\n⚠️  Some tests failed. Check knowledge base coverage and confidence scores.")

if __name__ == "__main__":
    main()
