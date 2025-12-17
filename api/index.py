from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from a2wsgi import ASGIMiddleware
import sys
import os

# Load environment variables (only in development, Vercel provides them automatically)
from dotenv import load_dotenv
import os

# Only load .env.local if not running on Vercel
if not os.environ.get("VERCEL"):
    load_dotenv(dotenv_path=".env.local")

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routers import chat, experts, metrics
from services import rag_service, expert_matcher, semantic_router, complexity_scorer

# Flag to track if services have been initialized
_services_initialized = False

def initialize_services():
    """Initialize all AI services (called on first request)"""
    global _services_initialized
    if _services_initialized:
        return
    
    print("🚀 Initializing AI services...")
    try:
        # Use centralized initialization from services/__init__.py
        from services import initialize_all
        success = initialize_all()
        
        if not success:
            print("⚠️ Some services failed to initialize, but continuing with fallbacks")
        
        _services_initialized = True
        print("✅ All services initialized successfully")
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        raise

app = FastAPI(
    title="Concierge AI API",
    description="Intelligent customer-to-expert routing system inspired by Intuit VEP",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def handle_vercel_routing(request: Request, call_next):
    # Initialize services on first request (lazy loading for Vercel)
    initialize_services()
    
    # Vercel passes the path as a query parameter when using rewrites
    if request.query_params.get("path"):
        # Reconstruct the correct path
        path = "/" + request.query_params.get("path")
        # Modify the scope directly
        request.scope["path"] = path
        request.scope["query_string"] = b""  # Clear query string
    
    print(f"🔍 Request path: {request.scope['path']}")
    print(f"🔍 Request method: {request.method}")
    response = await call_next(request)
    return response

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(experts.router, prefix="/experts", tags=["experts"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

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
