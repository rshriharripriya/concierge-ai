-- Simplified BM25 search function for PostgreSQL
-- This is a fallback function that uses PostgreSQL full-text search
-- to provide BM25-like functionality until the full schema migration is run

CREATE OR REPLACE FUNCTION bm25_search_knowledge_documents(
  query_text TEXT,
  match_count INT DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  content TEXT,
  metadata JSONB,
  bm25_score FLOAT,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  -- Check if content_tsv column exists
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'knowledge_documents' AND column_name = 'content_tsv'
  ) THEN
    -- Use tsvector column if it exists
    RETURN QUERY
    SELECT 
      kd.id,
      kd.title,
      kd.content,
      kd.metadata,
      ts_rank_cd(kd.content_tsv, websearch_to_tsquery('english', query_text)) AS bm25_score,
      kd.created_at
    FROM knowledge_documents kd
    WHERE kd.content_tsv @@ websearch_to_tsquery('english', query_text)
    ORDER BY bm25_score DESC
    LIMIT match_count;
  ELSE
    -- Fallback: use simple text matching
    RETURN QUERY
    SELECT 
      kd.id,
      kd.title,
      kd.content,
      kd.metadata,
      0.5::FLOAT AS bm25_score,  -- Mock score
      kd.created_at
    FROM knowledge_documents kd
    WHERE kd.content ILIKE '%' || query_text || '%'
    LIMIT match_count;
  END IF;
END;
$$ LANGUAGE plpgsql;
