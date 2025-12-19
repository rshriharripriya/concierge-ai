# Part 7: Backend & Serverless Engineering

## Overview
The backend is built with **FastAPI** but architected specifically for the **Vercel Serverless** environment. This requires a unique set of engineering patterns to handle statelessness, cold starts, and ephemeral file systems.

## 1. The Serverless Adapter
We do not use a standard `uvicorn` server in production. Instead, we use the `api/index.py` entry point which exposes the FastAPI app to Vercel's runtime.
*   **Challenge**: WSGI/ASGI bridging.
*   **Solution**: We use the **Vercel Rewrite Pattern** in `vercel.json` to route all `/api/py/*` requests to the single Python function, simulating a robust API server within a serverless function.

## 2. Cold Start Optimization
Serverless functions "sleep" after inactivity. Waking them up (Cold Start) can take seconds.
*   **Lazy Loading**: We delay the heavy imports (TensorFlow/Torch-heavy libraries) until the specific route needs them.
*   **Global State Caching**: We use `functools.lru_cache` for database connections and embedding models. This ensures that if a function instance is reused (Warm Start), we don't reconnect to Supabase, reducing latency from 2s to <200ms.

## 3. Asynchronous Concurrency
Python in a serverless environment can be blocking.
*   **Async/Await**: The entire RAG pipeline (`retrieve`, `rerank`, `generate`) is fully asynchronous. This allows the server to handle I/O (waiting for Groq/Supabase) without blocking the thread, maximizing throughput within the single-core serverless limit.
*   **Background Tasks**: We use `FastAPI.BackgroundTasks` for non-critical operations like "Faithfulness Scoring" or "Logging", ensuring the user gets their response immediately while the server finishes up housekeeping.
