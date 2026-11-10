"""
CORS middleware configuration
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from typing import List


def setup_cors(app: FastAPI, origins: List[str]) -> None:
    """
    Configure CORS middleware for the application
    
    Args:
        app: FastAPI application instance
        origins: List of allowed origins
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
