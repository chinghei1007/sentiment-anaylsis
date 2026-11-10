"""
Keyword Analysis API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime
import logging

from app.schemas.sentiment import TextRequest
from app.models.sentiment_model import model_manager
from app.core.keyword_analyzer import KeywordSentimentAnalyzer
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.api_prefix, tags=["keywords"])


# Initialize keyword analyzer (lazy loading)
_keyword_analyzer: KeywordSentimentAnalyzer = None


def get_keyword_analyzer():
    """Get or create keyword analyzer instance"""
    global _keyword_analyzer
    if _keyword_analyzer is None:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder \
            .appName("KeywordAnalyzer") \
            .getOrCreate()
        _keyword_analyzer = KeywordSentimentAnalyzer(spark)
    return _keyword_analyzer


@router.post("/keywords/analyze", response_model=Dict[str, Any])
async def analyze_keywords(request: TextRequest) -> Dict[str, Any]:
    """
    Analyze keywords in text for sentiment
    
    Request body:
    - text: Text to analyze
    
    Returns:
    - Keyword-level sentiment analysis
    """
    try:
        analyzer = get_keyword_analyzer()
        result = analyzer.calculate_document_keyword_scores(request.text)
        
        return {
            **result,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Keyword analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/keywords/batch", response_model=List[Dict[str, Any]])
async def batch_analyze_keywords(texts: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze keywords for multiple texts
    
    Request body:
    - texts: List of texts to analyze
    
    Returns:
    - List of keyword analysis results
    """
    try:
        analyzer = get_keyword_analyzer()
        results = []
        
        for text in texts:
            result = analyzer.calculate_document_keyword_scores(text)
            results.append({
                **result,
                "analyzed_at": datetime.now().isoformat()
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Batch keyword analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/keywords/trends", response_model=Dict[str, Any])
async def get_keyword_trends() -> Dict[str, Any]:
    """
    Get keyword sentiment trends from training data
    
    Returns:
    - Keyword sentiment trends
    """
    try:
        from pyspark.sql import SparkSession
        from app.core.dataset_parser import UnifiedDatasetLoader
        
        spark = SparkSession.builder \
            .appName("KeywordTrends") \
            .getOrCreate()
        
        loader = UnifiedDatasetLoader(spark)
        
        # Load training data
        df, metadata = loader.load(settings.train_data_path)
        
        # Analyze keyword trends
        analyzer = get_keyword_analyzer()
        trends = analyzer.analyze_keyword_sentiment_trends(
            df, 
            text_column="text",
            sentiment_column="sentiment"
        )
        
        # Convert to list
        trends_list = trends.collect()
        
        spark.stop()
        
        return {
            "trends": [
                {
                    "keyword": row.keyword,
                    "avg_sentiment": float(row.avg_sentiment),
                    "count": int(row.count)
                }
                for row in trends_list
            ],
            "total_keywords": len(trends_list),
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting keyword trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/keywords/top/{sentiment}", response_model=Dict[str, Any])
async def get_top_keywords(sentiment: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get top keywords by sentiment
    
    Path params:
    - sentiment: 'positive' or 'negative'
    
    Query params:
    - limit: Number of keywords to return
    
    Returns:
    - Top keywords for the specified sentiment
    """
    try:
        from pyspark.sql import SparkSession
        from app.core.dataset_parser import UnifiedDatasetLoader
        
        if sentiment not in ['positive', 'negative']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sentiment must be 'positive' or 'negative'"
            )
        
        spark = SparkSession.builder \
            .appName("TopKeywords") \
            .getOrCreate()
        
        loader = UnifiedDatasetLoader(spark)
        
        # Load training data
        df, metadata = loader.load(settings.train_data_path)
        
        # Get top keywords
        analyzer = get_keyword_analyzer()
        top_keywords = analyzer.extract_top_keywords_by_sentiment(
            df,
            text_column="text",
            sentiment_column="sentiment",
            top_n=limit
        )
        
        spark.stop()
        
        return {
            "sentiment": sentiment,
            "keywords": top_keywords.get(sentiment, []),
            "limit": limit,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting top keywords: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/keywords/frequency", response_model=Dict[str, Any])
async def get_keyword_frequency(limit: int = 20) -> Dict[str, Any]:
    """
    Get most frequent keywords
    
    Query params:
    - limit: Number of keywords to return
    
    Returns:
    - Most frequent keywords
    """
    try:
        from pyspark.sql import SparkSession
        from app.core.dataset_parser import UnifiedDatasetLoader
        
        spark = SparkSession.builder \
            .appName("KeywordFrequency") \
            .getOrCreate()
        
        loader = UnifiedDatasetLoader(spark)
        
        # Load training data
        df, metadata = loader.load(settings.train_data_path)
        
        # Get keyword frequency
        analyzer = get_keyword_analyzer()
        freq_df = analyzer.analyze_keyword_frequency(df, text_column="text", top_n=limit)
        
        freq_list = freq_df.collect()
        
        spark.stop()
        
        return {
            "keywords": [
                {
                    "keyword": row.keyword,
                    "frequency": int(row.frequency)
                }
                for row in freq_list
            ],
            "limit": limit,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting keyword frequency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
