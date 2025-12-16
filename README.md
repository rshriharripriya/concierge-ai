# Concierge AI - Intelligent Tax Assistant Platform

**Concierge AI** is a next-generation intelligent routing platform that revolutionizes how users get tax and financial help. By combining advanced AI with human expertise, it instantly analyzes every question and routes it to the perfect solution: lightning-fast AI responses for common queries or personalized expert assistance for complex scenarios.

Built with cutting-edge semantic routing, real-time RAG (Retrieval Augmented Generation), and intelligent expert matching, Concierge AI delivers the right answer, from the right source, at exactly the right time.

## ✨ What Makes This AWESOME

### Intelligent Query Classification
- **Semantic Intent Detection**: Advanced NLP models automatically classify user questions into categories like Simple Tax, Complex Tax, or Urgent scenarios
- **Dynamic Complexity Scoring**: Real-time analysis determines if a query needs AI assistance or human expertise
- **Context-Aware Routing**: Considers query complexity, confidence levels, and user intent for optimal routing decisions

### Hybrid AI + Human Architecture
- **AI Agent Mode**: Handles routine tax questions instantly using RAG-powered responses grounded in a comprehensive vector knowledge base
- **Expert Matching System**: Automatically matches complex queries to the best-suited human expert based on specialization, availability, and match confidence
- **Seamless Handoff**: Smooth transitions between AI and human assistance ensure users always get the best possible help

### Production-Grade RAG Pipeline
- **Vector Knowledge Base**: Tax documents and financial information stored in Supabase with pgvector for ultra-fast semantic search
- **Contextual Retrieval**: Each AI response pulls relevant source documents in real-time to provide accurate, grounded answers
- **Source Attribution**: Every AI answer includes references to source documents for transparency and trust

### Premium User Experience
- **Glassmorphic UI**: Modern, responsive interface with smooth animations and premium design aesthetics
- **Real-Time Feedback**: Live analysis indicators show users how their query is being processed
- **Mobile-First Design**: Fully responsive experience optimized for all device sizes
- **Expert Profiles**: Rich expert cards with bios, specializations, and availability status

## 🛠️ Tech Stack

### Frontend Architecture
- **Next.js 14**: Latest App Router with server components for optimal performance
- **TypeScript**: Type-safe development with full IDE support
- **Tailwind CSS**: Utility-first styling with custom design system
- **Framer Motion**: Smooth, professional animations and transitions
- **Lucide Icons**: Modern, consistent icon library

### Backend & AI Infrastructure
- **FastAPI**: High-performance Python API framework with automatic documentation
- **LangChain**: Advanced LLM orchestration and chain management
- **Semantic Router**: Intent classification and query routing engine
- **Sentence Transformers**: State-of-the-art embeddings for semantic search
- **Groq LLM**: Ultra-fast inference with Llama 3 models
- **Supabase**: Serverless PostgreSQL with pgvector for vector operations

### DevOps & Deployment
- **Vercel**: Edge-optimized hosting with automatic deployments
- **Python Serverless Functions**: Backend deployed as Vercel serverless functions
- **Environment Management**: Secure secrets handling across environments

## 📁 Project Architecture

```
concierge-ai/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Landing page with hero, features, architecture
│   └── chat/              # Chat interface with AI/expert routing
├── components/            
│   ├── main/              # Main page components (Hero, Features, Footer)
│   ├── ui/                # Reusable UI components (Buttons, Cards, Effects)
│   └── sub/               # Sub-components and utilities
├── api/                   # FastAPI backend
│   ├── services/          # Core business logic (RAG, routing, matching)
│   ├── utils/             # Helper utilities (embeddings, database)
│   └── index.py           # Main API entry point
├── lib/                   # Frontend utilities and API clients
└── knowledge_data/        # Tax knowledge documents for RAG
```

## 🚀 Getting Started

### Prerequisites
- **Node.js 18+** - JavaScript runtime
- **Python 3.9+** - Backend runtime
- **Supabase Account** - For database and vector storage
- **Groq API Key** - For LLM inference
- **Hugging Face Token** - For embeddings API

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rshriharripriya/concierge-ai.git
   cd concierge-ai
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create `.env.local` in the project root:
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_service_role_key
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   
   # AI Service Keys
   GROQ_API_KEY=your_groq_api_key
   HF_TOKEN=your_huggingface_token
   
   # API Configuration
   NEXT_PUBLIC_API_URL=/api/py
   ```
   
   **Where to get these keys:**
   - **Supabase**: Sign up at [supabase.com](https://supabase.com) → Create project → Settings → API
   - **Groq**: Get free API key at [console.groq.com](https://console.groq.com)
   - **Hugging Face**: Sign up at [huggingface.co](https://huggingface.co) → Settings → Access Tokens

5. **Initialize the database**
   
   Run the Supabase schema setup:
   ```bash
   # Execute the SQL in your Supabase dashboard
   cat supabase_schema.sql
   ```

6. **Start development servers**
   
   ```bash
   # Frontend (runs on http://localhost:3000)
   npm run dev
   
   # Backend (in a separate terminal)
   source .venv/bin/activate
   python -m uvicorn api.index:app --reload --port 8000
   ```

## 🎯 Core Features Explained

### Semantic Routing Engine
The semantic router analyzes natural language queries to determine the best handling path. It evaluates:
- **Intent classification** (Simple Tax, Complex Tax, Investment, etc.)
- **Complexity scoring** (1-5 scale based on query difficulty)
- **Confidence levels** (How certain the system is about classification)
- **Routing decisions** (AI vs Human expert)

### RAG-Powered AI Responses
When a query routes to the AI agent:
1. Query is converted to embeddings using Sentence Transformers
2. Vector similarity search finds the most relevant tax documents
3. Retrieved context is sent to Groq Llama 3 for response generation
4. AI synthesizes an answer grounded in actual tax documentation
5. Response includes source citations for transparency

### Expert Matching Algorithm
For complex queries that need human expertise:
1. Query embeddings are compared against expert skill profiles
2. Semantic similarity scores determine best expert matches
3. Availability and match confidence are factored in
4. User sees expert profile with bio and specialization
5. Seamless handoff to human expert occurs

## 🎨 UI/UX Highlights

- **Glassmorphism Design**: Modern frosted glass effects with blur and transparency
- **Animated Beams**: Dynamic system architecture visualization with flowing data
- **Smooth Transitions**: Framer Motion animations for premium feel
- **Responsive Layout**: Mobile-first design that adapts to any screen size
- **Dark Mode Ready**: Elegant crimson theme with professional aesthetics

## 📊 Performance Optimization

- **Server Components**: Next.js server components reduce client bundle size
- **Code Splitting**: Automatic route-based code splitting
- **Vector Search**: Sub-100ms semantic search with pgvector
- **Edge Deployment**: Hosted on Vercel edge network for global low latency
- **Lazy Loading**: Components and images load on-demand

## 🔐 Security & Best Practices

- **Environment Variables**: Sensitive keys never exposed to client
- **Type Safety**: Full TypeScript coverage prevents runtime errors
- **SQL Injection Protection**: Parameterized queries via Supabase client
- **CORS Configuration**: Proper cross-origin resource sharing
- **API Rate Limiting**: Protection against abuse

## 🧪 Knowledge Base

The system includes pre-loaded tax knowledge covering:
- Standard deductions and tax brackets
- International student tax obligations
- Investment and capital gains taxation
- Tax credits and deductions
- Filing extensions and deadlines

## 🤝 Contributing

This is a portfolio project showcasing advanced AI engineering skills. Feel free to fork and build upon it!

## 📄 License

MIT License - See LICENSE file for details

---

**Built by Shri Harri Priya Ramesh** | [Portfolio](https://rshriharripriya.vercel.app) | [LinkedIn](https://linkedin.com/in/rshriharripriya)
