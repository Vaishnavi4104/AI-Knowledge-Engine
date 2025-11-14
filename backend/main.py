"""
AI Knowledge Engine for Smart Support & Ticket Resolution
FastAPI Backend Application

This is the main entry point for the FastAPI backend server.
"""

import logging
from contextlib import asynccontextmanager
from threading import Thread

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.database import create_tables
from app.routes.auth_routes import router as auth_router
from app.routes.ticket_routes import router as ticket_router
from app.routes.analytics_routes import router as analytics_router
from app.services.embedding_service import embedding_service
from app.services.language_service import language_service
from app.services.recommendation_service import recommendation_service
from app.services.topic_service import topic_service

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_models_in_background():
    """Load models in a background thread to avoid blocking server startup."""

    try:
        # Load embedding service (SentenceTransformer)
        logger.info("Loading embedding model: %s", embedding_service.model_name)
        embedding_service._load_model()

        # Load language detection service (FastText)
        logger.info("Loading FastText language detection model...")
        language_service._load_model()
        if language_service.is_model_loaded():
            logger.info("FastText model loaded successfully")
        else:
            logger.warning("FastText model not loaded, using fallback detection")

        # Initialize recommendation service (FAISS index)
        logger.info("Initializing recommendation service...")
        recommendation_service._load_or_build_index()
        if recommendation_service.index:
            logger.info(
                "FAISS index ready with %s vectors",
                recommendation_service.index.ntotal,
            )

        # Initialize topic service (BERTopic)
        logger.info("Initializing topic service...")
        topic_service._initialize_model()
        logger.info("BERTopic service initialized")

        logger.info("All models loaded successfully!")

    except Exception as exc:  # pragma: no cover - startup logging
        logger.exception("Error loading models: %s", exc)
        logger.warning("Some models may not be available")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: D401
    """Application lifespan manager (startup/shutdown hooks)."""

    logger.info("Starting AI Knowledge Engine Backend...")
    
    # Create database tables if they don't exist
    logger.info("Creating database tables...")
    create_tables()
    
    logger.info("Server starting... Models will load in background.")

    # Start model loading in background thread
    model_loading_thread = Thread(target=load_models_in_background, daemon=True)
    model_loading_thread.start()

    yield

    logger.info("Shutting down AI Knowledge Engine Backend...")
    logger.info("Cleaning up resources...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Backend API for AI-powered ticket analysis and resolution",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(ticket_router, prefix="/api", tags=["tickets"])
app.include_router(analytics_router, prefix="/api", tags=["analytics"])


@app.get("/")
async def root():
    """Root endpoint - Health check."""

    return {
        "message": f"{settings.app_name} Backend is running!",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment,
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):  # noqa: D401
    """Global HTTP exception handler."""

    logger.error("HTTP Exception: %s", exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):  # noqa: D401
    """Global exception handler for unexpected errors."""

    logger.exception("Unexpected error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


if __name__ == "__main__":
    """Run the application using uvicorn."""

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
