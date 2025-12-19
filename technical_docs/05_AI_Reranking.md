# Part 5: Neural Reranking

## Overview
Reranking is the "Secret Sauce" that makes our RAG production-grade. Traditional vector search (Bi-Encoder) is fast but lacks nuance. Reranking (Cross-Encoder) is slow but extremely accurate.

## Technology: Cohere Rerank v3
We integrate the **Cohere Rerank API** (`rerank-english-v3.0`) as a post-processing step.

## The "Two-Stage" Process

### Stage 1: Retrieval (Bi-Encoder)
*   **Goal**: Recall. Find *anything* that might be relevant.
*   **Algorithm**: Cosine Similarity in Vector Space.
*   **Volume**: We fetch top **30** documents.
*   **Speed**: < 100ms.

### Stage 2: Reranking (Cross-Encoder)
*   **Goal**: Precision. Rank the top 30 by true semantic relevance.
*   **Algorithm**: The model takes the Query and Document *together* as a single input pair and outputs a relevance logit.
    *   `Score(Query, Doc_A) -> 0.98`
    *   `Score(Query, Doc_B) -> 0.12`
*   **Volume**: We return top **5** to the LLM.

## Why this is critical for Tax
In tax law, "Deducting a car" (Business) vs "Deducting a car" (Charity) are semantically close in vector space but vastly different in rules. A Cross-Encoder can distinguish the nuance of the user's specific phrasing ("can I write off my donation of a car") much better than a simple vector dot product.

## Implementation Details
*   **File**: `api/services/reranker.py`
*   **Fallback**: If Cohere API fails or is disabled, the system gracefully falls back to the original vector similarity scores using the boolean flag `USE_RERANKING`.
