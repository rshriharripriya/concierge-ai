# Part 2: The Agentic RAG Pipeline

## Overview
Concierge AI moves beyond naive "Retrieve-Then-Generate" patterns. We implement an **Agentic RAG Pipeline** where the retrieval process is dynamic, multi-stage, and self-correcting.

## Pipeline Architecure

The `RAGService.generate_answer` method orchestrates a 4-step process:

### Step 1: Query Contextualization (The "De-Anonymizer")
Raw user questions are often context-dependent (e.g., "What about for trust funds?"). Searching this directly fails.
*   **Technique**: We use a specialized LLM call to rewrite the query based on `conversation_history`.
*   **Input**: `Chat History` + `Latest Query`
*   **Output**: A **Standalone Query** (e.g., "What are the tax implications for trust funds regarding 401k withdrawals?").
*   **Implementation**: `rag_service.contextualize_query()`

### Step 2: Hybrid Retrieval (The "Wide Net")
We query the Supabase Vector Store using a hybrid approach:
*   **Semantic Search**: Uses `content_embedding` (Cosine Similarity) to find conceptually related chunks.
*   **Keyword Filtering**: (Optional) Can filter by `metadata.category` if the Intent Classifier detected a specific domain (e.g., "Bookkeeping").
*   **Expansion**: We fetch `k=30` candidates initially, casting a wide net to ensure recall.

### Step 3: Neural Reranking (The "Precision Filter")
Retrieving 30 documents introduces noise. We pass these candidates to the **Cohere Rerank v3** model.
*   **Cross-Encoder**: The model scores the *pair* (Query, Document) for true relevance.
*   **Thresholding**: We discard any document with a relevance score < 0.5.
*   **Result**: The top 5 documents are mathematically guaranteed to be highly relevant.

### Step 4: Context Assembly (The "Smart Context")
We don't just dump text into the prompt. We assemble a structured context block:
*   We continuously add chunks until we hit `MAX_TOTAL_CONTEXT` (8000 tokens).
*   Each chunk is prefixed with `[Source X - Title]` to allow the LLM to cite it correctly.
*   We inject `relevance_score` into the context so the LLM knows which source to trust more.

## Why this is "Agentic"
It is agentic because the system **evaluates its own input** (Contextualization) and **evaluates its own retrieval** (Reranking) before generating a response. It doesn't blindly trust the user's phrasing or the database's first result.
