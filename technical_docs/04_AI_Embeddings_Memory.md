# Part 4: Embeddings & Conversational Memory

## 1. Vector Embeddings Strategy

### The Engine: Sentence Transformers
We use `sentence-transformers/all-MiniLM-L6-v2` for generating embeddings.
*   **Why?**: It offers the best balance of speed (essential for serverless) and performance for semantic search. It outputs **384-dimensional** vectors.
*   **Implementation**: Hosted via **HuggingFace Inference API** to offload computation from the Vercel serverless function (which has limited CPU).

### The Storage: Supabase & pgvector
We use **PostgreSQL** with the `pgvector` extension as our vector database.
*   **Schema**:
    ```sql
    create table knowledge_documents (
      id uuid primary key,
      content text,
      content_embedding vector(384),
      metadata jsonb
    );
    ```
*   **Search**: We utilize the `cosine` distance operator (`<=>`) within a custom RPC function `match_knowledge_documents`. This allows us to execute vector search *inside* the database, returning only the relevant rows to the Vercel backend.

## 2. Conversational Memory (Context Management)

Memory in RAG is tricky. We don't just feed the entire chat log into the prompt (context window limits).

### The "Sliding Window" Context
We maintain a sliding window of the last **6 messages** (3 turns).
*   **Storage**: Messages are stored in the `messages` table in Supabase, linked by `conversation_id`.
*   **Retrieval**: On every turn, `rag_service.get_conversation_history(limit=6)` fetches this window.

### Stateful Query Rewriting
Memory is actively used to *repair* queries (as described in Part 2).
*   **Scenario**: User says "No, the other one."
*   **Memory**: System looks at previous turn (Assistant: "You can file 1040 or 1040-SR").
*   **Rewritten**: "I want to know about the 1040-SR form."
This transformation turns "Short Term Memory" into "Actionable Search Intent."
