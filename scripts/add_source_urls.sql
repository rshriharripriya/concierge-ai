-- Add source URLs to knowledge base documents
-- Run these queries in Supabase SQL Editor to add links to your ingested books

-- Example 1: Add URL to a specific book by source name
UPDATE knowledge_documents
SET metadata = jsonb_set(
    metadata,
    '{source_url}',
    '"https://www.irs.gov/pub/irs-pdf/p519.pdf"',
    true
)
WHERE source = 'IRS Publication 519';

-- Example 2: Add URL to all documents from a specific book
UPDATE knowledge_documents
SET metadata = jsonb_set(
    metadata,
    '{source_url}',
    '"https://example.com/personal-finance-101"',
    true
)
WHERE metadata->>'book_name' = 'The Personal Finance 101 Boxed Set';

-- Example 3: Add URLs to multiple books at once
WITH book_urls AS (
    VALUES
        ('The Personal Finance 101 Boxed Set', 'https://example.com/personal-finance-101'),
        ('Tax Guide 2024', 'https://www.irs.gov/tax-guide-2024'),
        ('Home Office Deductions Guide', 'https://www.irs.gov/publications/p587')
)
UPDATE knowledge_documents AS kd
SET metadata = jsonb_set(
    kd.metadata,
    '{source_url}',
    to_jsonb(bu.column2),
    true
)
FROM book_urls AS bu
WHERE kd.metadata->>'book_name' = bu.column1;

-- View documents with their URLs
SELECT 
    title,
    source,
    metadata->>'chapter' as chapter,
    metadata->>'source_url' as source_url
FROM knowledge_documents
WHERE metadata->>'source_url' IS NOT NULL
LIMIT 10;

-- Check which books don't have URLs yet
SELECT DISTINCT
    metadata->>'book_name' as book_name,
    source,
    count(*) as chunk_count
FROM knowledge_documents
WHERE metadata->>'source_url' IS NULL
GROUP BY book_name, source
ORDER BY chunk_count DESC;
