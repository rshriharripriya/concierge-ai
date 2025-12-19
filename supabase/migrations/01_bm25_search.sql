-- Migration: Add BM25 Full-Text Search Support
-- Date: 2024-12-16
-- Purpose: Enable hybrid search (BM25 + vector) for better exact-term recall

-- ============================================
-- STEP 1: Add tsvector column and populate it
-- ============================================
ALTER TABLE knowledge_documents 
ADD COLUMN IF NOT EXISTS content_tsv tsvector;

UPDATE knowledge_documents 
SET content_tsv = to_tsvector('english', content)
WHERE content_tsv IS NULL;

-- ============================================
-- STEP 2: Create GIN index for fast search
-- ============================================
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_fts 
ON knowledge_documents USING GIN(content_tsv);

-- ============================================
-- STEP 3: Auto-update trigger
-- ============================================
CREATE OR REPLACE FUNCTION knowledge_documents_tsv_trigger() RETURNS trigger AS $$
BEGIN
  new.content_tsv := to_tsvector('english', coalesce(new.content, ''));
  RETURN new;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tsvectorupdate ON knowledge_documents;
CREATE TRIGGER tsvectorupdate 
BEFORE INSERT OR UPDATE ON knowledge_documents
FOR EACH ROW EXECUTE FUNCTION knowledge_documents_tsv_trigger();

-- ============================================
-- STEP 4: Hybrid search function (BM25 + Vector)
-- ============================================
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
    LIMIT match_count * 2
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

-- ============================================
-- STEP 5: Simplified BM25-only search function
-- ============================================
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
      0.5::FLOAT AS bm25_score,
      kd.created_at
    FROM knowledge_documents kd
    WHERE kd.content ILIKE '%' || query_text || '%'
    LIMIT match_count;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Verification
-- ============================================
COMMENT ON TABLE knowledge_documents IS 'Documents with BM25 full-text search and vector embeddings';
COMMENT ON COLUMN knowledge_documents.content_tsv IS 'Full-text search vector for BM25 ranking';
