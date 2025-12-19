# Part 1: AI Generation & LLM Strategy

## Overview
Concierge AI adopts a **Provider-Agnostic Generation Layer** powered by **LiteLLM**. This allows us to decouple the application logic from specific model providers, enabling hot-swapping between Groq (Llama 3), Google (Gemini 2.0), and OpenAI without code changes.

## 1. Core LLM Configuration
We primary use **Llama 3.3 70B** hosted on **Groq** for its exceptional inference speed (>300 tokens/sec), which is critical for maintaining conversational latency in a complex RAG pipeline.

### Configuration (`rag_service.py`)
```python
self.model = os.getenv("RAG_MODEL", "groq/llama-3.3-70b-versatile")
self.fallbacks = [
    "openrouter/google/gemini-2.0-flash-exp:free",
    "gpt-4o-mini"
]
```

## 2. Prompt Engineering Architecture
We use a **Strict Persona-Based Prompting** strategy to ensure high-fidelity financial advice.

### The "Tax Expert" System Prompt
The prompt enforces a specific output structure preventing common hallucination pitfalls:
1.  **Citation Enforcement**: Every claim must use `[1]` style brackets.
2.  **Uncertainty Handling**: "Only ask follow-ups when NECESSARY."
3.  **Complexity matching**: Brief answers for simple questions, detailed breakdowns for complex scenarios.

**Snippet:**
```text
Retrieved Context (ordered by relevance):
[Source 1 - Relevance: 0.85] Title: IRS Pub 501
[Source 2 - Relevance: 0.72] Title: 1040 Instructions

ANSWER RULES:
1. Prioritize Source 1
2. Match answer length to question complexity
3. ...
```

## 3. Resilience & Fallbacks
Using `litellm.completion`, we implement automatic retries and provider fallbacks. If Groq rate limits (429), the system transparently reroutes the request to Gemini 2.0 Flash via OpenRouter. This ensures 99.99% availability even during provider outages.

## 4. Response Streaming
While the current Vercel Serverless environment has 60s timeouts, the backend is architected to support streaming. However, for "Analysis" tasks (intent classification), we use blocking calls to ensure we receive valid JSON before proceeding.
