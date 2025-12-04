-- Drop existing indexes
DROP INDEX IF EXISTS idx_knowledge_embedding;
DROP INDEX IF EXISTS idx_conversations_embedding;
DROP INDEX IF EXISTS idx_experts_embedding;

-- Drop existing function
DROP FUNCTION IF EXISTS match_knowledge_documents;

-- Alter vector dimensions from 1536 to 384
ALTER TABLE knowledge_documents 
ALTER COLUMN content_embedding TYPE vector(384);

ALTER TABLE conversations 
ALTER COLUMN query_embedding TYPE vector(384);

ALTER TABLE experts 
ALTER COLUMN expertise_embedding TYPE vector(384);

-- Recreate indexes
CREATE INDEX idx_knowledge_embedding ON knowledge_documents 
  USING ivfflat (content_embedding vector_cosine_ops);

CREATE INDEX idx_conversations_embedding ON conversations 
  USING ivfflat (query_embedding vector_cosine_ops);

CREATE INDEX idx_experts_embedding ON experts 
  USING ivfflat (expertise_embedding vector_cosine_ops);

-- Recreate function with new dimensions
CREATE OR REPLACE FUNCTION match_knowledge_documents(
  query_embedding VECTOR(384),  -- Changed from 1536
  match_count INT DEFAULT 5,
  match_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  content TEXT,
  source TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    knowledge_documents.id,
    knowledge_documents.title,
    knowledge_documents.content,
    knowledge_documents.source,
    1 - (knowledge_documents.content_embedding <=> query_embedding) AS similarity
  FROM knowledge_documents
  WHERE 1 - (knowledge_documents.content_embedding <=> query_embedding) > match_threshold
  ORDER BY knowledge_documents.content_embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Clear existing embeddings (they're 1536-dim, incompatible with 384-dim)
UPDATE knowledge_documents SET content_embedding = NULL;
UPDATE conversations SET query_embedding = NULL;
UPDATE experts SET expertise_embedding = NULL;
