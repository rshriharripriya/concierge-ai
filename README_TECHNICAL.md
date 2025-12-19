# Concierge AI: Comprehensive Technical Report

> **"Chunk the parts and go deep"**

This repository contains a full breakdown of the Concierge AI architecture, split into 9 detailed technical documents as requested. This serves as the source of truth for engineering blogs and technical due diligence.

## 📂 Technical Documentation Series

### 🧠 AI Core Architecture
*   **[Part 1: AI Generation & LLM Strategy](technical_docs/01_AI_Generation.md)**
    *   *Topics*: Provider Agnostic Layer (LiteLLM), Llama 3 on Groq, Persona-based Prompt Engineering.
*   **[Part 2: The Agentic RAG Pipeline](technical_docs/02_AI_RAG.md)**
    *   *Topics*: The 4-Stage Pipeline (Contextualization -> Hybrid Retrieval -> Reranking -> Assembly).
*   **[Part 3: Multi-Agent Architecture](technical_docs/03_AI_Multi_Agent.md)**
    *   *Topics*: LLM Router Agent, Expert Matcher Agent, and Inter-Agent Handover Protocols.

### 🧩 Retrieval & Intelligence
*   **[Part 4: Embeddings & Conversational Memory](technical_docs/04_AI_Embeddings_Memory.md)**
    *   *Topics*: Supabase pgvector, Sentence Transformers (384d), Sliding Window Memory.
*   **[Part 5: Neural Reranking](technical_docs/05_AI_Reranking.md)**
    *   *Topics*: Cohere Cross-Encoders, Precision vs. Recall, Thresholding strategies.
*   **[Part 6: AI Evaluation (Ragas)](technical_docs/06_AI_Evaluation.md)**
    *   *Topics*: Faithfulness, Context Precision, Automated Eval Pipelines.

### 🏗️ Engineering & Infrastructure
*   **[Part 7: Backend & Serverless Engineering](technical_docs/07_Backend_Serverless.md)**
    *   *Topics*: Vercel Serverless optimization, Cold Start mitigation, Async Concurrency.
*   **[Part 8: Frontend & Premium UX](technical_docs/08_Frontend.md)**
    *   *Topics*: Glassmorphism, Framer Motion Physics, Optimistic UI updates.
*   **[Part 9: Data Ingestion & Scaling](technical_docs/09_Data_Ingestion.md)**
    *   *Topics*: Recursive Character Chunking, Chapter-Aware Retrieval, SHA-256 Deduplication.

---

## Quick System Stats
*   **Vector DB**: Supabase (PostgreSQL)
*   **LLM Provider**: Groq (Llama 3.3 70B)
*   **Response Time**: < 3.0s (Average)
*   **Embeddings**: `all-MiniLM-L6-v2`
*   **Framework**: Next.js 16 + FastAPI
