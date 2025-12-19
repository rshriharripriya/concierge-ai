# Evaluation Framework

## 🎯 Purpose

This framework provides **reproducible, automated testing** for the Concierge AI system. It measures:

- **Routing Accuracy**: AI vs Human routing decisions
- **Intent Classification**: Correct intent detection (simple_tax, complex_tax, urgent, etc.)
- **Complexity Scoring**: Mean Absolute Error on 1-5 complexity scale
- **Disambiguation Recall**: Detecting ambiguous queries needing clarification
- **Expert Matching**: Matching queries to correct expert specialties

## 📊 Quick Start

### Run All Tests

```bash
# From project root
cd evaluation
python run_evaluation.py
```

### Expected Output

```
🧪 Testing: simple_001
   Query: What is the standard deduction for 2024?
   Intent: simple_tax (expected: simple_tax) - PASS
   Route: ai (expected: ai) - PASS
   Complexity: 1 (expected: 1) - PASS

================================================================
EVALUATION RESULTS
================================================================

📊 METRICS:
   Routing Accuracy:        87.5%
   Intent Accuracy:         93.3%
   Complexity MAE:          0.4
   Disambiguation Recall:   100.0%
   Expert Match Accuracy:   80.0%

📈 SUMMARY:
   Total Tests:    15
   Passed:         13 ✅
   Failed:         2 ❌

🎯 OVERALL RATING: ✨ STRONG (7-8/10)
================================================================
```

## 📁 Files

### `golden_dataset.json`
Contains 15 carefully curated test cases covering:
- **Simple queries**: Standard deduction, W-2 forms, deadlines
- **Complex queries**: Multi-state tax, crypto, stock options
- **Urgent queries**: IRS audit notices, penalty letters  
- **Ambiguous queries**: "Can I deduct my car?" (missing context)
- **Specialty queries**: Bookkeeping, international tax, estate planning

Each test case includes:
```json
{
  "id": "simple_001",
  "query": "What is the standard deduction for 2024?",
  "expected_intent": "simple_tax",
  "expected_route": "ai",
  "expected_complexity": 1,
  "expected_answer_contains": ["14600", "single"]
}
```

### `run_evaluation.py`
Automated test runner that:
1. Initializes all backend services
2. Runs each test query through the full pipeline
3. Compares actual vs expected outcomes
4. Calculates aggregate metrics
5. Saves detailed results to `results_TIMESTAMP.json`

## 🔬 What Gets Tested

### 1. Query Validation & Disambiguation
- Detects ambiguous queries
- Returns clarifying questions
- Example: "Can I deduct my car?" → "Are you self-employed?"

### 2. LLM Routing Decision
- Intent classification (simple/complex/urgent)
- Complexity scoring (1-5 scale)
- Route decision (AI vs human)

### 3. Expert Matching  
- For human-routed queries
- Matches to correct specialty (audit, crypto, international)
- Validates match score

### 4. RAG Answer Quality
- For AI-routed queries
- Checks for expected keywords in answer
- Validates confidence score

## 📈 Interpreting Results

### Routing Accuracy
- **\u003e90%**: Expert-level routing
- **80-90%**: Strong production system
- **70-80%**: Good but needs improvement
- **\u003c70%**: Routing logic needs rework

### Intent Accuracy  
- **\u003e85%**: High-quality classification
- **75-85%**: Acceptable for production
- **\u003c75%**: Intent classifier needs improvement

### Complexity MAE
- **\u003c0.5**: Excellent calibration
- **0.5-1.0**: Good, within ±1 point tolerance
- **\u003e1.0**: Complexity scoring needs adjustment

## 🎯 Baseline vs Goal

| Metric | Baseline (6.5/10) | Goal (8.5/10) | How to Improve |
|--------|-------------------|---------------|----------------|
| Routing Accuracy | ~75% | \u003e90% | LLM-based intent classifier |
| Intent Accuracy | ~70% | \u003e90% | Few-shot prompting, better examples |
| Complexity MAE | ~1.2 | \u003c0.5 | Calibrated scoring, more test data |
| Disambiguation | ~50% | \u003e95% | Improved ambiguity detection |

## 🚀 Continuous Improvement

### Adding New Test Cases

1. Edit `golden_dataset.json`
2. Add new test case following the schema
3. Run evaluation to see impact

### A/B Testing Changes

```bash
# Baseline (before changes)
python run_evaluation.py
# Results saved to results_20241216_120000.json

# Make changes to routing logic
# ...

# Test again  
python run_evaluation.py
# Results saved to results_20241216_120500.json

# Compare results
python compare_results.py results_20241216_120000.json results_20241216_120500.json
```

## 🏆 Expert-Level Checklist

- [x] **Evaluation Framework**: Automated testing with golden dataset
- [x] **LLM Intent Classifier**: Replaces keyword regex matching
- [x] **Reproducible Metrics**: JSON results with timestamps
- [ ] **Query Disambiguation**: Detect ambiguous queries (in progress)
- [ ] **100+ Test Cases**: Expand golden dataset
- [ ] **Continuous Monitoring**: Track metrics over time
- [ ] **A/B Testing**: Compare routing strategies

## 📦 Results Archive

All evaluation runs are saved to `results_TIMESTAMP.json` with:
- Full test results for each query
- Pass/fail status per test
- Aggregate metrics
- Timestamp for tracking improvement over time

---

**Pro Tip**: Run evaluation before AND after every major change to prove improvements with data, not claims.
