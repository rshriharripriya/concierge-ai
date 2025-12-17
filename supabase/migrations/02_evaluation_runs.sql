-- Migration: Create Evaluation Runs Table
-- Date: 2024-12-16
-- Purpose: Store evaluation metrics for RAGAS and routing accuracy

CREATE TABLE IF NOT EXISTS evaluation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- RAGAS Metrics (stored as 0.0-1.0 decimals)
    faithfulness DECIMAL(5,4),           -- Answer faithfulness to context
    context_precision DECIMAL(5,4),      -- Precision of retrieved context
    context_recall DECIMAL(5,4),         -- Recall of retrieved context
    context_relevancy DECIMAL(5,4),      -- Relevancy of retrieved context
    answer_relevancy DECIMAL(5,4),       -- Relevancy of generated answer
    
    -- Routing Metrics (stored as 0.0-1.0 decimals)
    routing_accuracy DECIMAL(5,4),       -- LLM-based routing accuracy
    routing_accuracy_baseline DECIMAL(5,4), -- Keyword routing baseline
    intent_accuracy DECIMAL(5,4),        -- Intent classification accuracy
    complexity_mae DECIMAL(4,2),         -- Mean absolute error for complexity
    disambiguation_recall DECIMAL(4,3),  -- Recall for disambiguation queries
    
    -- Test Summary
    total_tests INTEGER,
    tests_passed INTEGER,
    tests_failed INTEGER,
    
    -- Full Results (JSON for detailed breakdown)
    detailed_results JSONB,
    
    -- Metadata
    evaluation_note TEXT
);

-- Index for fetching latest results efficiently
CREATE INDEX idx_evaluation_runs_created_at ON evaluation_runs(created_at DESC);

-- Add table comment
COMMENT ON TABLE evaluation_runs IS 'Stores evaluation run results for metrics dashboard and performance tracking';
