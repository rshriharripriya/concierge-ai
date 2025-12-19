# Evaluation Framework

## 🎯 Purpose

This framework provides **reproducible, automated testing** for the Concierge AI system. It measures:

- **Routing Accuracy**: AI vs Human routing decisions
- **Intent Classification**: Correct intent detection (simple_tax, complex_tax, urgent, etc.)
- **Complexity Scoring**: Mean Absolute Error on 1-5 complexity scale
- **Disambiguation Recall**: Detecting ambiguous queries needing clarification
- **Expert Matching**: Matching queries to correct expert specialties

## 📊 Quick Start


### Prerequisites

```bash
# Install development dependencies (includes Ragas & LangChain)
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# From project root
python evaluation/run_evaluation.py --force --ragas
```

**Flags:**
- `--force`: Bypass the one-week cooldown period (useful for development)
- `--ragas`: Enable expensive Ragas evaluation (context precision, faithfulness, etc.)
- `--rerun-failed`: Only retry tests that failed in the last run

### Expected Output

```
Testing: simple_001
Query: What is the standard deduction for 2024?
Intent: simple_tax (expected: simple_tax) - PASS
Route: ai (expected: ai) - PASS
Complexity: 1 (expected: 1) - PASS

================================================================
EVALUATION RESULTS
================================================================

METRICS:
Routing Accuracy:        87.5%
Intent Accuracy:         93.3%
Complexity MAE:          0.4
Disambiguation Recall:   100.0%
Expert Match Accuracy:   80.0%

SUMMARY:
Total Tests:    15
Passed:         13 
Failed:         2 

OVERALL RATING: STRONG (7-8/10)
================================================================
```

## Files

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
5. Saves detailed results to Supabase (`evaluation_runs` table)

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
 python evaluation/run_evaluation.py
 # Results saved to Supabase (Record ID: 123)
 
 # Make changes to routing logic
 # ...
 
 # Test again  
 python evaluation/run_evaluation.py
 # Results saved to Supabase (Record ID: 124)
 
 # Compare results
 # Check the Metric History visualization in the frontend or query Supabase directly
 ```

## 🏆 Expert-Level Checklist

- [x] **Evaluation Framework**: Automated testing with golden dataset
- [x] **LLM Intent Classifier**: Replaces keyword regex matching
- [x] **Reproducible Metrics**: JSON results with timestamps
- [ ] **100+ Test Cases**: Expand golden dataset



## 📦 Results Archive

All evaluation runs are saved directly to the **Supabase** `evaluation_runs` table with:
- Full test results for each query
- Pass/fail status per test
- Aggregate metrics
- Ragas scores (if enabled)
- Timestamp for tracking improvement over time

You can query the results history via the `evaluation_runs` table or the metrics API endpoints.

---

**Pro Tip**: Run evaluation before AND after every major change to prove improvements with data.
