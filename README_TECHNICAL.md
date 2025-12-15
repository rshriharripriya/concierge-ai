# Concierge AI: Detailed Technical Overview

## Project Vision & Context

**Concierge AI** is an intelligent customer-to-expert routing system directly inspired by Intuit's Virtual Expert Platform (VEP) architecture. The project demonstrates a production-grade implementation of agentic AI workflows that automatically triage customer inquiries, attempt autonomous AI resolution, and intelligently escalate to human experts when needed. Built specifically to showcase capabilities relevant to Intuit's Software Engineer I role on the VEP team, it addresses the real-world challenge of scaling expert access while maintaining service quality across millions of customer interactions.

The system solves a critical problem in financial services: **how do you provide personalized tax and bookkeeping expertise to customers when simple questions can be answered instantly by AI, but complex scenarios require human judgment?** Traditional chatbots fail at this because they can't assess their own limitations or make nuanced routing decisions.

***

## System Architecture

### Multi-Stage Intelligent Routing Pipeline

The architecture implements a **four-stage decision pipeline** that processes every customer query:

**Stage 1: Intent Classification**  
Uses a semantic routing engine built on embedding-based similarity matching. When a query arrives, it's embedded into a 384-dimensional vector space using HuggingFace's `sentence-transformers/all-MiniLM-L6-v2` model and compared against pre-defined intent categories (simple_tax, complex_tax, bookkeeping, urgent, general). Rather than keyword matching, this approach understands semantic meaning—"When's my return due?" and "What's the deadline for filing?" both route to the same intent despite different wording. The semantic router maintains a library of example utterances for each category and uses cosine similarity to determine the best match with confidence scoring.

**Stage 2: Complexity Scoring**  
A heuristic-based scoring engine analyzes queries along multiple dimensions to assign a complexity score from 1 to 5. The system examines keyword patterns (urgency indicators like "audit," "deadline," technical terms like "cryptocurrency," "foreign income"), query structure (length, multiple questions, numerical references), and intent type. Scores of 4-5 automatically trigger expert escalation. This component is optimized for serverless environments—instead of calling an LLM for each complexity assessment (which adds latency and cost), it uses fast pattern matching with intelligent rules derived from tax domain expertise.

**Stage 3: RAG-Based Response Generation with Conversational Memory**  
The Retrieval-Augmented Generation layer attempts to answer queries autonomously using grounded knowledge and conversation history. The system implements sophisticated **conversational memory** through query contextualization—before retrieving documents, follow-up questions are rewritten using conversation history to create standalone queries. For example, "what about bitcoin?" following "is crypto taxable?" becomes "Is bitcoin taxable?" ensuring accurate retrieval.

When a query enters this stage, it's embedded and used to perform vector similarity search against a knowledge base of tax documents, IRS publications, and financial guides stored in Supabase's pgvector database. The top 5 most relevant documents (similarity threshold >0.4) are retrieved and injected into a prompt template alongside the user's query and conversation history. 

A **Llama 3.3 70B** model (accessed via Groq's API) generates responses using an optimized prompt that enforces:
- Extreme conciseness (bullet points, short paragraphs)
- Numbered citations (`[1]`, `[2]`) instead of verbose source tags
- Acknowledgment of uncertainty when appropriate

The system calculates confidence using the **maximum similarity score** among retrieved documents (boosted by 1.5x to account for MiniLM's lower raw scores), rather than average—this better reflects the quality of the best match. If the AI suggests "consult an expert," confidence is automatically downgraded to <0.7.

**Stage 4: Expert Matching & Assignment**  
When queries fail confidence thresholds (complexity ≥4, AI confidence <0.60, or explicit urgency), the expert matching engine activates. This component implements a sophisticated multi-factor scoring algorithm that evaluates available experts across four dimensions: specialty alignment (40% weight), availability status (30% weight), performance metrics (20% weight), and semantic similarity (10% weight). The system returns the highest-scoring expert with estimated wait time, biographical information, and specialty tags.

***

## Technical Stack Deep Dive

### Frontend: Premium User Experience with Interactive Citations

The interface is built on **Next.js 16.0.7** (with React 19.2.1 for security patches) using the App Router architecture for React Server Components, enabling partial pre-rendering and streaming responses. The design system implements **glassmorphism aesthetics**—layered translucent glass panels with backdrop-filter blur effects, multi-color gradient overlays (blue, violet, pink, purple spectrums), and subtle noise textures for depth. Every interactive element features micro-animations powered by **Framer Motion**, including spring-based hover states, ripple effects, staggered fade-in animations, and continuous gradient position shifts.

**Enhanced Chat Interface**: Messages display rich metadata badges showing intent classification, complexity scores, and AI confidence levels. The chat bubble component uses **ReactMarkdown** with **remark-gfm** to render formatted responses including:
- Bullet points and numbered lists
- Bold text for emphasis
- Inline code snippets
- Links with proper styling

**Interactive Source Citations**: Sources are presented in an expandable "Show Sources" section at the bottom of each AI response. Instead of cluttering the chat with full citations, users can click a toggle button (with book icon and chevron) to reveal:
- Numbered source titles matching in-text citations
- Similarity match percentages (e.g., "85% match")
- Source attribution (Internal vs. external references)
- Smooth animation effects using Tailwind's `animate-in` utilities

When experts are matched, the UI renders detailed profile cards with avatars, specialties, biographical context, and estimated response times—all animated with glass-card entrance effects.

### Backend: Serverless AI Orchestration

The backend runs on **FastAPI** deployed as Vercel serverless functions using **a2wsgi** for ASGI-to-WSGI adaptation (replacing the previous Mangum adapter which was AWS Lambda-specific). This architecture demands careful optimization:

**Lazy Service Initialization**: Since Vercel's WSGI environment doesn't support FastAPI's `lifespan` events, services initialize on the **first request** using a global `_services_initialized` flag. This middleware-based approach ensures:
- Services only initialize once per function instance
- Cold starts are detectable (logs show `🚀 Initializing AI services...`)
- Subsequent requests skip initialization entirely
- Thread-safe initialization prevents race conditions

Heavy objects like LLM clients, embedding models, and database connections are cached using Python's `functools.lru_cache` decorator to survive across invocations within the same runtime instance.

**Path Routing for Vercel**: The API implements custom middleware to handle Vercel's rewrite behavior. Requests to `/api/py/chat/query` are rewritten to `/api?path=chat/query`, and the middleware reconstructs the correct path `/chat/query` before FastAPI's router processes it. This enables clean URL namespacing without breaking serverless function isolation.

**Environment Variable Management**: The `.env.local` file is only loaded in development (when `VERCEL` environment variable is absent). In production, Vercel automatically injects environment variables, eliminating the need for file-based configuration.

The API exposes RESTful endpoints for query processing, conversation retrieval, and expert lookup. Each request follows the four-stage pipeline, with services communicating through in-memory Python objects. The entire query processing flow completes in under 3 seconds on warm invocations.

### AI/ML Components

**Semantic Router**: Built using the semantic-router library with HuggingFace Inference API embeddings. Routes are defined declaratively with example utterances, and the encoder automatically positions them in vector space. At runtime, query embeddings are compared against route vectors using cosine similarity.

**RAG Pipeline with Query Contextualization**: Implements an enhanced retrieval-augmented generation pattern:
1. **Conversation History Retrieval**: Fetches the last 5 messages from the conversation
2. **Query Contextualization**: If history exists, uses Llama 3.3 to rewrite the query as a standalone question
3. **Document Retrieval**: Embeds the standalone query and performs vector similarity search
4. **Context Augmentation**: Combines retrieved documents with conversation history in the LLM prompt
5. **Response Generation**: Llama 3.3 generates concise, cited responses
6. **Confidence Calculation**: Uses max similarity score × 1.5 boost factor

This architecture transforms the system from a stateless Q&A bot into a conversational agent that maintains context across multiple turns.

**Document Chunking Strategy**: The ingestion pipeline splits knowledge files using `=== DOCUMENT` delimiters, creating granular embeddings for specific topics (e.g., "NFT Taxation" as a standalone document within a larger file). This dramatically improves retrieval accuracy for niche queries.

**LLM Selection**: Uses Groq's API to access Llama 3.3 70B, providing near-GPT-4 quality at zero cost with extremely fast inference. The system includes failover logic and timeout protections to handle API errors gracefully.

### Database Architecture: Vector-Native Design

**Supabase PostgreSQL** serves as the central data store with the **pgvector extension** enabling native vector operations. The database schema includes four core tables:

**experts**: Stores human expert profiles with specialty arrays, biographical text, avatar URLs, availability status (JSONB for flexible scheduling), and performance metrics (ratings, interaction counts, resolution rates). The expertise_embedding column (VECTOR 384) holds semantic representations of expert capabilities.

**knowledge_documents**: The RAG knowledge base with title, content, source attribution, category tags, and content_embedding vectors (384 dimensions). A function-based index on cosine similarity enables fast approximate nearest neighbor search. The `match_knowledge_documents` PostgreSQL function (similarity threshold: 0.4) encapsulates vector search logic.

**conversations**: Tracks each customer interaction with fields for user_id, original query, query_embedding, classified intent, complexity_score, route_decision (ai vs. human), AI response text, confidence scores, assigned expert ID, and status. The context JSONB field stores reasoning and urgency flags.

**messages**: Stores the full message thread with role (user/assistant/expert), content, metadata (including sources for AI responses), and timestamps. Foreign key relationship to conversations enables efficient conversation history retrieval.

***

## Data Flow & Execution

### Request Lifecycle

1. User types a question in the glassmorphism chat interface
2. Frontend calls `sendQuery()` from the API utility library (`/lib/api.ts`)
3. HTTP POST to `/api/py/chat/query` (Vercel rewrites to `/api?path=chat/query`)
4. Middleware reconstructs path and initializes services on first request
5. FastAPI deserializes request into Pydantic `QueryRequest` model
6. `process_query` handler orchestrates the four-stage pipeline:
   - Semantic router classifies intent using embedding similarity
   - Complexity scorer analyzes keywords, structure, and urgency
   - RAG service retrieves conversation history
   - Query contextualization rewrites follow-ups as standalone questions
   - Vector search retrieves top 5 knowledge documents (similarity >0.4)
   - Llama 3.3 generates response with numbered citations
   - Confidence calculation uses max similarity × 1.5
   - Routing decision evaluates complexity, confidence, urgency
   - Expert matcher scores candidates on multi-factor algorithm (if escalating)
7. Conversation and messages saved to Supabase
8. FastAPI returns `QueryResponse` with sources array
9. Frontend displays message with:
   - Markdown rendering (bullets, bold, links)
   - Numbered citations in text
   - Expandable "Show Sources" section
   - Expert profile card (if matched)
10. `conversation_id` persisted for next turn

### Vector Similarity Search Mechanics

PostgreSQL's pgvector extension performs cosine similarity search in 384-dimensional space. The `match_knowledge_documents` function calculates `1 - (embedding <=> query_embedding)` for all documents, filters by threshold (0.4), sorts by similarity descending, and limits to top 5. This server-side function reduces network overhead.

***

## Deployment & Infrastructure

### Vercel Full-Stack Serverless

Both frontend and backend deploy to **Vercel** in a monorepo configuration:

**Frontend**: Next.js builds into static/server-rendered pages with App Router optimizations

**Backend**: FastAPI serverless functions with:
- **a2wsgi adapter** for ASGI-to-WSGI conversion (not Mangum)
- **Lazy initialization** via middleware (not lifespan events)
- **Path reconstruction** from Vercel's query parameter rewrites
- 1GB memory allocation, 60-second timeout
- Python 3.12 runtime

**Routing Configuration** (`vercel.json`):
```json
{
  "rewrites": [{
    "source": "/api/py/:path*",
    "destination": "/api?path=:path*"
  }]
}
```

**Cold Start Optimization**: 
- Services initialize on first request (2-4 second penalty)
- Subsequent requests reuse warm instances (~500ms)
- Cached LLM clients, embeddings, database connections
- Pre-warming through test queries at startup

**Scalability**: Vercel auto-scales by spawning function instances. Each request is isolated with no shared state. Connection pooling in Supabase handles concurrent queries.

### Security & Configuration

- Environment variables injected by Vercel at runtime
- No `.env.local` in production (conditional loading)
- Secrets stored in Vercel dashboard (HF_TOKEN, GROQ_API_KEY, SUPABASE credentials)
- CORS configured for cross-origin requests
- React upgraded to 19.2.1 for CVE-2025-55182 security patch

***

## Key Technical Achievements

**Advanced Conversational AI**: Multi-turn dialogue with query contextualization, ensuring follow-up questions retrieve accurate information by rewriting them as standalone queries using conversation history.

**Production-Grade RAG Optimization**: 
- Document chunking strategy for granular retrieval
- Max similarity scoring instead of average (better confidence signals)
- Numbered citations for cleaner UX
- Expandable source attribution

**Serverless Architecture Mastery**: 
- Solved Vercel-specific challenges (lifespan unsupported, path rewrites)
- Lazy initialization pattern for WSGI environments
- a2wsgi adapter for proper ASGI-to-WSGI conversion
- Sub-3-second warm response times

**Interactive Source Attribution**: Novel UI pattern showing numbered citations in text with expandable source details—balances transparency with readability.

**Premium UI/UX Engineering**: Glassmorphism design, ReactMarkdown rendering, Framer Motion animations, expandable components with smooth transitions.

**Vector Database Proficiency**: Full implementation of pgvector—from schema design through embedding generation to similarity queries with custom PostgreSQL functions.

**Multi-Factor Decision Systems**: Expert matching algorithm combining semantic similarity, availability, performance metrics, and urgency weighting.

**End-to-End Full-Stack Ownership**: Single developer implemented React/Next.js frontend, FastAPI/Python backend, PostgreSQL/pgvector database, LangChain RAG pipeline, Groq LLM integration, and Vercel deployment—demonstrating versatility valued at Intuit.

This project directly demonstrates capabilities for Intuit's VEP role: building intelligent routing systems, integrating LLM-based AI, designing scalable cloud architectures, optimizing serverless functions, and creating user-centric experiences that connect customers with expertise—exactly what the Virtual Expert Platform team builds for 100 million TurboTax, QuickBooks, and Credit Karma users.
