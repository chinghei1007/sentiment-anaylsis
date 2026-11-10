"""
Schemas for sentiment analysis API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SentimentLabel(str, Enum):
    """Sentiment label enumeration"""
    POSITIVE = "positive"
    NEGATIVE = "negative"


class TextRequest(BaseModel):
    """Request schema for text sentiment analysis"""
    text: str = Field(..., min_length=1, max_length=10000, 
                      description="Text to analyze for sentiment")


class BatchTextRequest(BaseModel):
    """Request schema for batch sentiment analysis"""
    texts: List[str] = Field(..., min_length=1, max_length=100,
                               description="List of texts to analyze")


class SentimentPrediction(BaseModel):
    """Schema for sentiment prediction result"""
    text: str
    sentiment: SentimentLabel
    label: int  # 1=positive, 0=negative
    confidence: Optional[float] = None
    prob_positive: Optional[float] = None
    prob_negative: Optional[float] = None
    
    class Config:
        use_enum_values = True


class BatchSentimentResponse(BaseModel):
    """Response schema for batch predictions"""
    predictions: List[SentimentPrediction]
    total: int
    processed_at: datetime


class TrainingRequest(BaseModel):
    """Request schema for model training"""
    model_type: str = Field(default="logistic", 
                            description="Type of classifier: logistic, naive_bayes, random_forest, gbt")
    validation_split: float = Field(default=0.2, ge=0.1, le=0.5,
                                     description="Fraction of data to use for validation")
    random_seed: int = Field(default=42, description="Random seed for reproducibility")


class TrainingResponse(BaseModel):
    """Response schema for training results"""
    model_type: str
    training_samples: int
    validation_samples: int
    label_distribution: Dict[str, int]
    accuracy: float
    confusion_matrix: Dict[int, Dict[int, int]]
    sample_predictions: List[Dict[str, Any]]
    timestamp: datetime
    model_saved: bool
    model_path: Optional[str] = None


class EvaluationResponse(BaseModel):
    """Response schema for model evaluation"""
    accuracy: float
    f1_score: float
    precision: float
    recall: float
    confusion_matrix: Dict[int, Dict[int, int]]
    total_samples: int
    positive_samples: int
    negative_samples: int
    evaluated_at: datetime


class ModelInfo(BaseModel):
    """Schema for model information"""
    model_type: str
    trained: bool
    training_date: Optional[datetime] = None
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    path: Optional[str] = None


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    version: str
    timestamp: datetime
    spark_available: bool
    model_loaded: bool


class DatasetInfo(BaseModel):
    """Schema for dataset information"""
    name: str
    total_samples: int
    positive_samples: int
    negative_samples: int
    neutral_samples: int
    sources: List[str]
    columns: List[str]
