"""
AI Knowledge Engine for Smart Support & Ticket Resolution
FastAPI Backend Application

This is the main entry point for the FastAPI backend server.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager
import asyncio
from threading import Thread

from app.routes.ticket_routes import router as ticket_router
from app.services.embedding_service import embedding_service
from app.services.language_service import language_service
from app.services.recommendation_service import recommendation_service
from app.services.topic_service import topic_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_models_in_background():
    """
    Load models in a background thread to avoid blocking server startup.
    """
    try:
        # Load embedding service (SentenceTransformer)
        logger.info("Loading SentenceTransformer model...")
        embedding_service._load_model()
        logger.info(f"Embedding model loaded: {embedding_service.model_name}")
        
        # Load language detection service (FastText)
        logger.info("Loading FastText language detection model...")
        language_service._load_model()
        if language_service.is_model_loaded():
            logger.info("FastText model loaded successfully")
        else:
            logger.warning("FastText model not loaded, using fallback detection")
        
        # Initialize recommendation service (FAISS index)
        logger.info("Initializing FAISS recommendation service...")
        recommendation_service._load_or_build_index()
        logger.info(f"FAISS index ready with {recommendation_service.index.ntotal if recommendation_service.index else 0} vectors")
        
        # Initialize topic service (BERTopic)
        logger.info("Initializing BERTopic service...")
        topic_service._initialize_model()
        logger.info("BERTopic service initialized")
        
        logger.info("All models loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        logger.warning("Some models may not be available")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Knowledge Engine Backend...")
    logger.info("Server starting... Models will load in background.")
    
    # Start model loading in background thread
    model_loading_thread = Thread(target=load_models_in_background, daemon=True)
    model_loading_thread.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Knowledge Engine Backend...")
    logger.info("Cleaning up resources...")


# Create FastAPI application
app = FastAPI(
    title="AI Knowledge Engine",
    description="Backend API for AI-powered ticket analysis and resolution",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ticket_router, prefix="/api", tags=["tickets"])


@app.get("/")
async def root():
    """
    Root endpoint - Health check
    """
    return {
        "message": "AI Knowledge Engine Backend is running!",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "AI Knowledge Engine Backend",
        "version": "1.0.0"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Global HTTP exception handler
    """
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Global exception handler for unexpected errors
    """
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


if __name__ == "__main__":
    """
    Run the application using uvicorn
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
