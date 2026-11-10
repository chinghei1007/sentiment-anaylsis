"""
Configuration settings for sentiment analysis application
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Sentiment Analysis API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = Path("/workspace/github__rskworld__sentiment-analysis/data")
    models_dir: Path = base_dir / "models"
    
    # Training data paths
    train_data_path: str = str(data_dir / "train_data.csv")
    test_data_path: str = str(data_dir / "test_data.csv")
    full_data_path: str = str(data_dir / "sentiment_data.csv")
    
    # Model settings
    model_type: str = "logistic"
    model_save_path: str = str(models_dir / "sentiment_model")
    
    # API
    api_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()

# Ensure directories exist
settings.models_dir.mkdir(parents=True, exist_ok=True)
