-- Create evaluation_runs table to store evaluation results
CREATE TABLE IF NOT EXISTS evaluation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- RAGAS Metrics (stored as 0.0-1.0 decimals)
    faithfulness DECIMAL(5,4),      -- 0.0000 to 1.0000
    context_precision DECIMAL(5,4),
    context_recall DECIMAL(5,4),
    context_relevancy DECIMAL(5,4),
    answer_relevancy DECIMAL(5,4),
    
    -- Routing Metrics (stored as 0.0-1.0 decimals)
    routing_accuracy DECIMAL(5,4),
    routing_accuracy_baseline DECIMAL(5,4),
    intent_accuracy DECIMAL(5,4),
    complexity_mae DECIMAL(4,2),
    disambiguation_recall DECIMAL(4,3),
    
    -- Test Summary
    total_tests INTEGER,
    tests_passed INTEGER,
    tests_failed INTEGER,
    
    -- Full Results (JSON for detailed breakdown)
    detailed_results JSONB,
    
    -- Metadata
    evaluation_note TEXT
);

-- Index for fetching latest
CREATE INDEX idx_evaluation_runs_created_at ON evaluation_runs(created_at DESC);

-- Add comment
COMMENT ON TABLE evaluation_runs IS 'Stores evaluation run results for metrics dashboard';
