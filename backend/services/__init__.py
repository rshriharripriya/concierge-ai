"""
Service initialization module.
Initializes all AI services for the backend.
"""
import logging

logger = logging.getLogger(__name__)

def initialize_all():
    """Initialize all backend services"""
    logger.info("🚀 Initializing backend services...")
    
    # Initialize in dependency order
    try:
        # Base services
        from services import semantic_router
        semantic_router.initialize()
        logger.info("✓ Semantic router (fallback) initialized")
        
        # New LLM router with fallback
        from services import llm_router
        llm_router.initialize(fallback_router=semantic_router.service_instance)
        logger.info("✓ LLM router initialized")
        
        # LLM Intent Classifier
        from services import llm_intent_classifier
        llm_intent_classifier.initialize()
        logger.info("✓ LLM intent classifier initialized")
        
        # Query validator
        from services import query_validator
        query_validator.initialize()
        logger.info("✓ Query validator initialized")
        
        # RAG components
        from services import rag_service
        rag_service.initialize()
        logger.info("✓ RAG service initialized")
        
        # Reranker
        from services import reranker
        reranker.initialize()
        logger.info("✓ Reranker initialized")
        
        # Expert matcher
        from services import expert_matcher
        expert_matcher.initialize()
        logger.info("✓ Expert matcher initialized")
        
        logger.info("✅ All services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
