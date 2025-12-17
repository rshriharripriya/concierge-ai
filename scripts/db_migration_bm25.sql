-- Migration: Add BM25 Full-Text Search Support to knowledge_documents
-- Date: 2024-12-16
-- Purpose: Enable hybrid search (BM25 + vector) for better exact-term recall

-- Step 1: Add tsvector column for full-text search
ALTER TABLE knowledge_documents 
ADD COLUMN IF NOT EXISTS content_tsv tsvector;

-- Step 2: Populate tsvector column with existing content
UPDATE knowledge_documents 
SET content_tsv = to_tsvector('english', content)
WHERE content_tsv IS NULL;

-- Step 3: Create GIN index for fast full-text search
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_fts 
ON knowledge_documents USING GIN(content_tsv);

-- Step 4: Create trigger to auto-update tsvector on insert/update
CREATE OR REPLACE FUNCTION knowledge_documents_tsv_trigger() RETURNS trigger AS $$
begin
  new.content_tsv := to_tsvector('english', coalesce(new.content, ''));
  return new;
end
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tsvectorupdate ON knowledge_documents;
CREATE TRIGGER tsvectorupdate 
BEFORE INSERT OR UPDATE ON knowledge_documents
FOR EACH ROW EXECUTE FUNCTION knowledge_documents_tsv_trigger();

-- Step 5: Create BM25 search function
-- This function combines BM25 full-text search with vector similarity
CREATE OR REPLACE FUNCTION hybrid_search_knowledge_documents(
  query_text TEXT,
  query_embedding vector(384),
  match_count INT DEFAULT 10,
  bm25_weight FLOAT DEFAULT 0.5,
  vector_weight FLOAT DEFAULT 0.5
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  content TEXT,
  metadata JSONB,
  bm25_score FLOAT,
  similarity FLOAT,
  combined_score FLOAT
) AS $$
BEGIN
  RETURN QUERY
  WITH bm25_results AS (
    SELECT 
      kd.id,
      kd.title,
      kd.content,
      kd.metadata,
      ts_rank_cd(kd.content_tsv, websearch_to_tsquery('english', query_text)) AS bm25_score
    FROM knowledge_documents kd
    WHERE kd.content_tsv @@ websearch_to_tsquery('english', query_text)
  ),
  vector_results AS (
    SELECT 
      kd.id,
      kd.title,
      kd.content,
      kd.metadata,
      1 - (kd.embedding <=> query_embedding) AS similarity
    FROM knowledge_documents kd
    ORDER BY kd.embedding <=> query_embedding
    LIMIT match_count * 2  -- Get more for fusion
  )
  SELECT 
    COALESCE(b.id, v.id) AS id,
    COALESCE(b.title, v.title) AS title,
    COALESCE(b.content, v.content) AS content,
    COALESCE(b.metadata, v.metadata) AS metadata,
    COALESCE(b.bm25_score, 0.0) AS bm25_score,
    COALESCE(v.similarity, 0.0) AS similarity,
    (COALESCE(b.bm25_score, 0.0) * bm25_weight + 
     COALESCE(v.similarity, 0.0) * vector_weight) AS combined_score
  FROM bm25_results b
  FULL OUTER JOIN vector_results v ON b.id = v.id
  ORDER BY combined_score DESC
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Verification queries
-- Check if tsvector column was created and populated
SELECT 
  COUNT(*) as total_docs,
  COUNT(content_tsv) as docs_with_tsv
FROM knowledge_documents;

-- Test BM25 search with websearch_to_tsquery (handles natural language + quotes)
-- Example: 'taxes for "F-1 students"' will correctly handle the quoted phrase
SELECT 
  title,
  ts_rank_cd(content_tsv, websearch_to_tsquery('english', 'taxes for "F-1 students"')) AS score
FROM knowledge_documents
WHERE content_tsv @@ websearch_to_tsquery('english', 'taxes for "F-1 students"')
ORDER BY score DESC
LIMIT 5;
