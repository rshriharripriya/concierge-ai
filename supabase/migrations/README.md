# Database Migrations

This directory contains SQL migrations for the Concierge AI database. Migrations are numbered and should be run in order.

## Migration Files

### `01_bm25_search.sql`
**Purpose**: Add BM25 full-text search capability to `knowledge_documents` table

**What it does**:
- Adds `content_tsv` tsvector column for full-text indexing
- Creates GIN index for fast full-text search
- Sets up auto-update trigger to keep tsvector in sync
- Creates `hybrid_search_knowledge_documents()` function combining BM25 + vector similarity
- Creates `bm25_search_knowledge_documents()` for BM25-only search with fallback

**When to run**: After initial table creation, before enabling hybrid search

---

### `02_evaluation_runs.sql`
**Purpose**: Create table to store evaluation metrics

**What it does**:
- Creates `evaluation_runs` table with fields for:
  - RAGAS metrics (faithfulness, context precision/recall/relevancy, answer relevancy)
  - Routing metrics (accuracy, intent accuracy, complexity MAE)
  - Test summary (total/passed/failed counts)
  - Detailed JSON results
- Creates index on `created_at` for efficient latest-results queries

**When to run**: Before running evaluation scripts

---

### `03_populate_experts.sql`
**Purpose**: Populate expert profiles with initial data

**What it does**:
- Updates existing 5 experts with avatar URLs
- Inserts 10 new expert profiles (estate planning, startup tax, real estate, etc.)
- Uses `ON CONFLICT DO NOTHING` to avoid duplicates

**When to run**: After `experts` table exists (initial schema)

**Note**: Update avatar URLs to match your Supabase project before running

---

## How to Run Migrations

### Option 1: Supabase Dashboard
1. Go to your Supabase project → SQL Editor
2. Copy the contents of each migration file
3. Run them in order (01, 02, 03)

### Option 2: Supabase CLI
```bash
# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Apply all migrations
supabase db push
```

### Option 3: Direct SQL
```bash
psql "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres" < supabase/migrations/01_bm25_search.sql
psql "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres" < supabase/migrations/02_evaluation_runs.sql
psql "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres" < supabase/migrations/03_populate_experts.sql
```

---

## Migration Status

Check which migrations have been applied:

```sql
-- Check if BM25 is set up
SELECT 
  EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'knowledge_documents' AND column_name = 'content_tsv'
  ) as bm25_enabled;

-- Check evaluation_runs table
SELECT COUNT(*) as total_evaluations FROM evaluation_runs;

-- Check expert profiles
SELECT COUNT(*) as total_experts FROM experts;
```

---

## Notes

- All migrations are idempotent (safe to run multiple times)
- `create_evaluation_runs.sql` in this directory is legacy and superseded by `02_evaluation_runs.sql`
- Expert avatar URLs need to be updated to match your Supabase Storage bucket
