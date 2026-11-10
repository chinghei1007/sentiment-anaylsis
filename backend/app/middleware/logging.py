"""
Logging middleware for request/response tracking
"""

import logging
import time
from fastapi import Request, Response
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details"""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url} | "
            f"Headers: {dict(request.headers)}"
        )
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} | "
                f"Duration: {duration:.4f}s | "
                f"Endpoint: {request.url.path}"
            )
            
            # Add duration header
            response.headers["X-Response-Time"] = f"{duration:.4f}s"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {str(e)} | "
                f"Duration: {duration:.4f}s | "
                f"Endpoint: {request.url.path}"
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle errors consistently"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle errors"""
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}")
            return Response(
                content={"error": str(e)},
                status_code=500,
                media_type="application/json"
            )
