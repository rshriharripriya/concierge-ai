-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Experts table
CREATE TABLE experts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    specialties TEXT[] NOT NULL,
    expertise_embedding VECTOR(1536),
    bio TEXT,
    avatar_url TEXT,
    availability JSONB DEFAULT '{"status": "available", "schedule": {}}',
    performance_metrics JSONB DEFAULT '{"avg_rating": 0, "total_interactions": 0, "resolution_rate": 0}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    query TEXT NOT NULL,
    query_embedding VECTOR(1536),
    intent TEXT,
    complexity_score DECIMAL(3,2),
    route_decision TEXT CHECK (route_decision IN ('ai', 'human')),
    ai_response TEXT,
    ai_confidence DECIMAL(3,2),
    assigned_expert_id UUID REFERENCES experts(id),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'escalated')),
    context JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('user', 'assistant', 'expert')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge base (RAG documents)
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_embedding VECTOR(1536),
    source TEXT,
    category TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_experts_embedding ON experts USING ivfflat (expertise_embedding vector_cosine_ops);
CREATE INDEX idx_conversations_embedding ON conversations USING ivfflat (query_embedding vector_cosine_ops);
CREATE INDEX idx_knowledge_embedding ON knowledge_documents USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);

-- Function for vector similarity search
CREATE OR REPLACE FUNCTION match_knowledge_documents(
  query_embedding VECTOR(1536),
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

-- Seed sample experts
INSERT INTO experts (name, email, specialties, bio, avatar_url) VALUES
('Sarah Chen', 'sarah@concierge.ai', ARRAY['tax', 'small_business', 'schedule_c'], 'CPA with 10+ years experience in small business taxation', 'https://i.pravatar.cc/150?img=1'),
('Marcus Rodriguez', 'marcus@concierge.ai', ARRAY['tax', 'crypto', 'capital_gains'], 'Tax specialist focusing on cryptocurrency and investment taxation', 'https://i.pravatar.cc/150?img=12'),
('Emily Thompson', 'emily@concierge.ai', ARRAY['bookkeeping', 'quickbooks', 'payroll'], 'Certified bookkeeper specializing in QuickBooks and payroll services', 'https://i.pravatar.cc/150?img=5'),
('David Kim', 'david@concierge.ai', ARRAY['tax', 'international', 'foreign_income'], 'International tax consultant with expertise in expat taxation', 'https://i.pravatar.cc/150?img=15'),
('Lisa Patel', 'lisa@concierge.ai', ARRAY['bookkeeping', 'financial_planning', 'cash_flow'], 'Financial advisor helping businesses optimize cash flow', 'https://i.pravatar.cc/150?img=9');

-- Seed sample knowledge documents
INSERT INTO knowledge_documents (title, content, source, category) VALUES
('Standard Deduction 2024', 'The standard deduction for 2024 is $14,600 for single filers and $29,200 for married couples filing jointly. This amount is adjusted annually for inflation.', 'IRS Publication 17', 'tax'),
('Tax Filing Deadlines', 'Individual tax returns are due by April 15th each year. If April 15th falls on a weekend or holiday, the deadline is the next business day. Extensions can be requested until October 15th.', 'IRS.gov', 'tax'),
('QuickBooks Setup', 'To set up QuickBooks Online: 1) Create your account, 2) Enter business information, 3) Connect bank accounts, 4) Set up chart of accounts, 5) Import existing data if applicable.', 'QuickBooks Guide', 'bookkeeping'),
('Cryptocurrency Taxation', 'Cryptocurrency is treated as property by the IRS. Capital gains tax applies when you sell, trade, or use crypto. Short-term gains (held < 1 year) are taxed as ordinary income. Long-term gains have preferential rates.', 'IRS Notice 2014-21', 'tax'),
('Schedule C Deductions', 'Common Schedule C deductions for self-employed individuals include: home office expenses (if qualified), vehicle expenses, supplies, professional services, advertising, insurance, and business travel.', 'IRS Schedule C Instructions', 'tax');
