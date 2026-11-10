"""
Sentiment Analysis API - Main Application
FastAPI backend for sentiment analysis on user comments
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
import logging
import uvicorn
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import app components
from app.core.config import settings
from app.models.sentiment_model import model_manager

# Import routes
from app.routes.sentiment import router as sentiment_router
from app.routes.keywords import router as keywords_router

# Import middleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.cors import setup_cors


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        # Sentiment Analysis API
        
        Analyze sentiment of user comments and text using PySpark ML models.
        
        ## Features
        
        * **Document-level sentiment**: Classify entire texts as positive/negative
        * **Keyword-level analysis**: Analyze sentiment of individual keywords
        * **Batch processing**: Analyze multiple texts at once
        * **Model training**: Train custom models on your datasets
        * **Flexible dataset parsing**: Support for CSV, JSON, TSV, and common formats
        
        ## Quick Start
        
        1. **Predict sentiment**: POST `/api/v1/predict` with `{"text": "Your text here"}`
        2. **Train model**: POST `/api/v1/train` with model parameters
        3. **Evaluate model**: POST `/api/v1/evaluate`
        
        ## Dataset Formats
        
        The API supports various dataset formats:
        - CSV with configurable columns
        - JSON files
        - TSV files
        - Amazon review format
        - Twitter/social media format
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Setup CORS
    setup_cors(app, settings.cors_origins)
    
    # Include routers
    app.include_router(sentiment_router)
    app.include_router(keywords_router)
    
    # Add static files (for serving frontend in production)
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint"""
        return {
            "message": "Sentiment Analysis API",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/v1/health"
        }
    
    # Error handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle uncaught exceptions"""
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)},
        )
    
    return app


# Create application instance
app = create_app()


# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Sentiment Analysis API...")
    
    # Initialize model manager
    model_manager.initialize()
    
    # Try to load existing model
    success, message = model_manager.load_model()
    if success:
        logger.info(f"Model loaded: {message}")
    else:
        logger.warning(f"No model found, will train on first request: {message}")
    
    logger.info("API startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Sentiment Analysis API...")
    model_manager.shutdown()
    logger.info("API shutdown complete")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
