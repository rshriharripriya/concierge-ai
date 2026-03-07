-- Migration: Add Temporal Tax Year Extraction
-- Date: 2026-02-11
-- Purpose: Extract tax years from document text and store in metadata
--          for temporal ranking in hybrid retrieval

-- ============================================
-- STEP 1: Function to extract all years from document text
-- ============================================
CREATE OR REPLACE FUNCTION extract_all_tax_years(text_content TEXT)
RETURNS INTEGER[] AS $$
DECLARE
    all_years INTEGER[];
    year_text TEXT;
    extracted_year INTEGER;
    current_year INTEGER := EXTRACT(YEAR FROM CURRENT_DATE);
BEGIN
    FOR year_text IN 
        SELECT unnest(regexp_matches(text_content, '\b(20\d{2})\b', 'g'))
    LOOP
        extracted_year := year_text::INTEGER;
        IF extracted_year BETWEEN 2000 AND current_year + 1 THEN
            IF NOT (extracted_year = ANY(all_years)) THEN
                all_years := array_append(all_years, extracted_year);
            END IF;
        END IF;
    END LOOP;
    
    all_years := ARRAY(SELECT unnest(all_years) ORDER BY 1 DESC);
    RETURN all_years;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- STEP 2: Function to get primary (most recent) year
-- ============================================
CREATE OR REPLACE FUNCTION get_primary_tax_year(text_content TEXT)
RETURNS INTEGER AS $$
DECLARE
    all_years INTEGER[];
BEGIN
    all_years := extract_all_tax_years(text_content);
    IF array_length(all_years, 1) > 0 THEN
        RETURN all_years[1];
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- STEP 3: Update all existing documents with tax year metadata
-- ============================================
UPDATE knowledge_documents
SET metadata = COALESCE(metadata, '{}'::jsonb) || 
    jsonb_build_object(
        'tax_years', to_jsonb(extract_all_tax_years(title || ' ' || source || ' ' || LEFT(content, 1000))),
        'primary_tax_year', get_primary_tax_year(title || ' ' || source || ' ' || LEFT(content, 1000)),
        'is_current', get_primary_tax_year(title || ' ' || source || ' ' || LEFT(content, 1000)) >= EXTRACT(YEAR FROM CURRENT_DATE)
    );

-- ============================================
-- Verification: Check extracted years
-- ============================================
-- Run this SELECT to verify (won't affect migration):
-- SELECT 
--     title,
--     metadata->'tax_years' as all_years,
--     metadata->>'primary_tax_year' as primary_year,
--     metadata->>'is_current' as is_current
-- FROM knowledge_documents
-- WHERE metadata->'tax_years' IS NOT NULL
-- ORDER BY (metadata->>'primary_tax_year')::INTEGER DESC NULLS LAST
-- LIMIT 10;
