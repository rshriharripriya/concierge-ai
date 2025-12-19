# Part 9: Data Ingestion & "Big Data" Techniques

## Overview
A RAG system is only as good as its data. Our ingestion engine (`scripts/ingest_books.py`) implements advanced chunking strategies to handle large financial texts (PDFs, Books) without losing semantic meaning.

## 1. Recursive Character Chunking
We don't simply split by every 500 characters (which breaks sentences). We use `RecursiveCharacterTextSplitter`:
*   **Hierarchy**: It tries to split by `\n\n` (Paragraphs) first. If that's too big, it tries `\n` (Lines), then `. ` (Sentences).
*   **Result**: Chunks are grammatically complete and semantically coherent.
*   **Size**: We target **700 tokens** with **150 token overlap**. The overlap ensures reliable retrieval at the boundaries of chunks.

## 2. Chapter-Aware Ingestion
Flat lists of chunks lose the "Big Picture".
*   **Detection**: The script runs Regex patterns (`^Chapter \d+`) to detect module boundaries.
*   **Metadata Tagging**: Every chunk is stamped with `metadata.chapter = "Chapter 4: Deductions"`.
*   **Big Data Technique**: This enables "scoped retrieval". During RAG, if we match a chunk in "Chapter 4", we can query Supabase for *all other chunks* in Chapter 4, effectively loading the entire topic into the LLM's context window ("Context Expansion").

## 3. Deduplication (SHA-256)
To allow idempotent runs (re-running the script without duplicating data):
*   We compute a **SHA-256 hash** of the content `hashlib.sha256(text)`.
*   We check the database `metadata->>content_hash` index.
*   If the hash exists, `ingest_books.py` skips the insertion. This allows us to "resume" interrupted ingestion jobs on massive datasets without creating duplicates.
