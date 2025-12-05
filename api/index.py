from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from a2wsgi import ASGIMiddleware
import sys
import os
from contextlib import asynccontextmanager

# Env vars loaded below

from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routers import chat, experts
from services import rag_service, expert_matcher, semantic_router, complexity_scorer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize services
    print("🚀 Starting up... Initializing AI services")
    rag_service.initialize()
    expert_matcher.initialize()
    semantic_router.initialize()
    complexity_scorer.initialize()
    yield
    # Shutdown: Clean up if needed
    print("🛑 Shutting down...")

app = FastAPI(
    title="Concierge AI API",
    description="Intelligent customer-to-expert routing system inspired by Intuit VEP",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(experts.router, prefix="/experts", tags=["experts"])

@app.get("/")
async def root():
    return {
        "message": "Concierge AI API v1.0",
        "status": "operational",
        "description": "AI-powered triage and expert matching system"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "serverless": True}

# Vercel serverless handler
# Only wrap in ASGIMiddleware if running on Vercel (WSGI)
# Local uvicorn needs the raw ASGI app
if os.environ.get("VERCEL"):
    app = ASGIMiddleware(app)
