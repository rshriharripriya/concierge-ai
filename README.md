# Concierge AI

**Concierge AI** is an intelligent routing system designed to seamlessly connect user queries—specifically tax and financial questions—to the perfect resolution path: either an AI assistant for instant answers or a specialized human expert for complex scenarios.

Inspired by Intuit's Virtual Expert Platform (VEP) architecture, this project demonstrates advanced semantic routing, RAG (Retrieval Augmented Generation), and real-time expert matching.

![System Architecture](./public/architecture-preview.png)
*(Note: Ensure you have an architecture image or reference the live component)*

## 🚀 Key Features

-   **Intelligent Routing**: Automatically classifies queries by intent (e.g., "Simple Tax", "Complex Tax", "Urgent") and complexity.
-   **Hybrid Resolution**:
    -   **AI Agent**: Handles routine queries using RAG with a vector knowledge base.
    -   **Human Expert**: Routes complex or high-stakes issues to the best-matched human expert based on skills and availability.
-   **Real-time RAG**: Retrieves relevant tax documents from a Supabase vector store to ground AI responses.
-   **Modern UI**: A premium, responsive interface built with Next.js, Tailwind CSS, and Framer Motion.

## 🛠️ Tech Stack

### Frontend
-   **Framework**: Next.js 14 (App Router)
-   **Styling**: Tailwind CSS, Framer Motion
-   **Components**: Lucide React, Custom Glassmorphism UI

### Backend
-   **API**: FastAPI (Python)
-   **AI/ML**: LangChain, Semantic Router, Sentence Transformers
-   **LLM**: Groq (Llama 3)
-   **Database**: Supabase (PostgreSQL + pgvector)

## 📂 Project Structure

This project is structured as a monorepo for separated deployment:

-   `app/`: Next.js Frontend code.
-   `backend/`: FastAPI Backend code (Python).
-   `components/`: React UI components.
-   `lib/`: Shared utilities and API clients.

## ⚡️ Getting Started

### Prerequisites
-   Node.js 18+
-   Python 3.9+
-   Supabase Account
-   Groq API Key

### Local Development

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/rshriharripriya/concierge-ai.git
    cd concierge-ai
    ```

2.  **Install Frontend Dependencies**:
    ```bash
    npm install
    ```

3.  **Set up Backend**:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

4.  **Environment Variables**:
    Create a `.env.local` file in the root and add:
    ```env
    NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_key
    GROQ_API_KEY=your_groq_key
    ```

5.  **Run Locally**:
    -   **Frontend**: `npm run dev` (http://localhost:3000)
    -   **Backend**: `python uvicorn backend.api.index:app --reload` (http://127.0.0.1:8000)

## 📦 Deployment

This project is designed to be deployed as **two separate Vercel projects** (Frontend and Backend) to optimize performance and manage dependency sizes.

👉 **[Read the Deployment Guide](DEPLOYMENT_SEPARATED.md)** for step-by-step instructions.

## 📄 License

This project is licensed under the MIT License.
