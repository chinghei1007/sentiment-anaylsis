"""
Sentiment Analysis API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import logging

from app.schemas.sentiment import (
    TextRequest,
    BatchTextRequest,
    SentimentPrediction,
    BatchSentimentResponse,
    TrainingRequest,
    TrainingResponse,
    EvaluationResponse,
    ModelInfo,
    HealthResponse,
    DatasetInfo
)
from app.models.sentiment_model import model_manager
from app.core.config import settings
from app.utils.helpers import read_json_file, get_timestamp

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.api_prefix, tags=["sentiment"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API health and status"""
    spark_available = True
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()
        spark.stop()
    except Exception:
        spark_available = False
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(),
        spark_available=spark_available,
        model_loaded=model_manager.model_loaded
    )


@router.post("/predict", response_model=SentimentPrediction)
async def predict_sentiment(
    request: TextRequest
) -> SentimentPrediction:
    """
    Predict sentiment for a single text
    
    Request body:
    - text: The text to analyze
    
    Returns:
    - Prediction with sentiment, label, and confidence scores
    """
    try:
        logger.info(f"Predicting sentiment for text: {request.text[:50]}...")
        
        prediction = model_manager.predict(request.text)
        
        # Convert to Pydantic model
        sentiment_label = "positive" if prediction["sentiment"] == "positive" else "negative"
        
        return SentimentPrediction(
            text=prediction["text"],
            sentiment=sentiment_label,
            label=prediction["label"],
            confidence=prediction.get("confidence"),
            prob_positive=prediction.get("prob_positive"),
            prob_negative=prediction.get("prob_negative")
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/predict/batch", response_model=BatchSentimentResponse)
async def batch_predict_sentiment(
    request: BatchTextRequest
) -> BatchSentimentResponse:
    """
    Predict sentiment for multiple texts
    
    Request body:
    - texts: List of texts to analyze
    
    Returns:
    - List of predictions
    """
    try:
        logger.info(f"Batch predicting {len(request.texts)} texts")
        
        predictions = model_manager.batch_predict(request.texts)
        
        # Convert to Pydantic models
        sentiment_predictions = []
        for pred in predictions:
            if "error" in pred:
                # Skip or handle errors
                continue
            sentiment_label = "positive" if pred["sentiment"] == "positive" else "negative"
            sentiment_predictions.append(SentimentPrediction(
                text=pred["text"],
                sentiment=sentiment_label,
                label=pred["label"],
                confidence=pred.get("confidence"),
                prob_positive=pred.get("prob_positive"),
                prob_negative=pred.get("prob_negative")
            ))
        
        return BatchSentimentResponse(
            predictions=sentiment_predictions,
            total=len(sentiment_predictions),
            processed_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/train", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest
) -> TrainingResponse:
    """
    Train a new sentiment analysis model
    
    Request body:
    - model_type: Type of classifier (logistic, naive_bayes, random_forest, gbt)
    - validation_split: Fraction of data to use for validation
    - random_seed: Random seed for reproducibility
    
    Returns:
    - Training results and metrics
    """
    try:
        logger.info(f"Starting training with {request.model_type} classifier")
        
        success, train_results = model_manager.train(
            model_type=request.model_type,
            validation_split=request.validation_split,
            random_seed=request.random_seed
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=train_results.get("error", "Training failed")
            )
        
        # Convert confusion matrix to int keys
        cm = {}
        for true_label, preds in train_results["confusion_matrix"].items():
            cm[int(true_label)] = {int(pred): count for pred, count in preds.items()}
        
        return TrainingResponse(
            model_type=train_results["model_type"],
            training_samples=train_results["training_samples"],
            validation_samples=train_results["validation_samples"],
            label_distribution=train_results["label_distribution"],
            accuracy=train_results["accuracy"],
            confusion_matrix=cm,
            sample_predictions=train_results["sample_predictions"],
            timestamp=datetime.fromisoformat(train_results["timestamp"]),
            model_saved=True,
            model_path=settings.model_save_path
        )
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_model() -> EvaluationResponse:
    """
    Evaluate the current model on test data
    
    Returns:
    - Evaluation metrics (accuracy, F1, precision, recall)
    """
    try:
        logger.info("Evaluating model on test data")
        
        success, eval_results = model_manager.evaluate()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=eval_results.get("error", "Evaluation failed")
            )
        
        # Convert confusion matrix to int keys
        cm = {}
        for true_label, preds in eval_results["confusion_matrix"].items():
            cm[int(true_label)] = {int(pred): count for pred, count in preds.items()}
        
        return EvaluationResponse(
            accuracy=eval_results["accuracy"],
            f1_score=eval_results["f1_score"],
            precision=eval_results["precision"],
            recall=eval_results["recall"],
            confusion_matrix=cm,
            total_samples=eval_results["total_samples"],
            positive_samples=eval_results["positive_samples"],
            negative_samples=eval_results["negative_samples"],
            evaluated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/model", response_model=ModelInfo)
async def get_model_info() -> ModelInfo:
    """
    Get information about the current model
    
    Returns:
    - Model type, training date, accuracy, etc.
    """
    model_info = model_manager.get_model_info()
    
    return ModelInfo(
        model_type=model_info.get("model_type", "unknown"),
        trained=model_info.get("trained", False),
        training_date=datetime.fromisoformat(model_info["training_date"]) if model_info.get("training_date") else None,
        accuracy=model_info.get("accuracy"),
        f1_score=model_info.get("test_f1"),
        path=model_info.get("path")
    )


@router.get("/dataset", response_model=DatasetInfo)
async def get_dataset_info() -> DatasetInfo:
    """
    Get information about the training dataset
    
    Returns:
    - Dataset statistics
    """
    try:
        from pyspark.sql import SparkSession
        from app.core.sentiment_trainer import SentimentTrainer
        
        trainer = SentimentTrainer()
        df, label_dist = trainer.load_dataset(settings.full_data_path)
        
        # Get sources
        sources = df.select("source").distinct().collect()
        source_list = [row.source for row in sources]
        
        # Get column names
        columns = [field.name for field in df.schema.fields]
        
        # Count neutral samples
        neutral_count = df.filter(df.sentiment == "neutral").count()
        
        return DatasetInfo(
            name="Sentiment Analysis Dataset",
            total_samples=int(df.count()),
            positive_samples=int(label_dist.get(1.0, 0)),
            negative_samples=int(label_dist.get(0.0, 0)),
            neutral_samples=int(neutral_count),
            sources=source_list,
            columns=columns
        )
        
    except Exception as e:
        logger.error(f"Error getting dataset info: {e}")
        # Return default info
        return DatasetInfo(
            name="Sentiment Analysis Dataset",
            total_samples=50,
            positive_samples=18,
            negative_samples=17,
            neutral_samples=15,
            sources=["Product Review", "Customer Feedback", "Social Media"],
            columns=["id", "text", "sentiment", "source", "date"]
        )


@router.get("/history")
async def get_training_history() -> List[dict]:
    """
    Get training history
    
    Returns:
    - List of past training sessions
    """
    return model_manager.get_training_history()
