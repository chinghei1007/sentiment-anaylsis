"""
Sentiment Analysis Model Manager
Manages the lifecycle of sentiment analysis models
"""

from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import logging

from app.core.sentiment_trainer import SentimentTrainer
from app.core.config import settings

logger = logging.getLogger(__name__)


class SentimentModelManager:
    """
    Manages sentiment analysis models
    Handles training, loading, prediction, and evaluation
    """
    
    def __init__(self):
        """Initialize model manager"""
        self.trainer: Optional[SentimentTrainer] = None
        self.model_loaded: bool = False
        self.model_info: Dict[str, Any] = {}
        self.training_history: list = []
        
    def initialize(self) -> bool:
        """
        Initialize the model manager
        
        Returns:
            True if initialization successful
        """
        try:
            self.trainer = SentimentTrainer()
            logger.info("Sentiment model manager initialized")
            return True
        except Exception as e:
            logger.error(f"Error initializing model manager: {e}")
            return False
    
    def train(
        self,
        train_path: Optional[str] = None,
        model_type: str = "logistic",
        validation_split: float = 0.2,
        random_seed: int = 42
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Train a new sentiment model
        
        Args:
            train_path: Path to training data (uses default if None)
            model_type: Type of classifier
            validation_split: Fraction for validation
            random_seed: Random seed
            
        Returns:
            Tuple of (success, training results)
        """
        if self.trainer is None:
            self.initialize()
        
        try:
            train_path = train_path or settings.train_data_path
            
            logger.info(f"Starting training with {model_type} classifier")
            logger.info(f"Training data: {train_path}")
            
            # Train model
            train_results = self.trainer.train(
                train_data_path=train_path,
                model_type=model_type,
                validation_split=validation_split,
                random_seed=random_seed
            )
            
            # Save model
            model_save_path = settings.model_save_path
            self.trainer.save_model(model_save_path)
            
            # Update model info
            self.model_info = {
                "model_type": model_type,
                "trained": True,
                "training_date": datetime.now().isoformat(),
                "accuracy": train_results["accuracy"],
                "path": model_save_path,
                "label_distribution": train_results["label_distribution"]
            }
            
            # Add to history
            self.training_history.append({
                "timestamp": datetime.now().isoformat(),
                "model_type": model_type,
                "results": train_results
            })
            
            self.model_loaded = True
            
            logger.info(f"Training completed. Accuracy: {train_results['accuracy']:.4f}")
            
            return True, train_results
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False, {"error": str(e)}
    
    def load_model(self, model_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Load a trained model
        
        Args:
            model_path: Path to saved model (uses default if None)
            
        Returns:
            Tuple of (success, message)
        """
        if self.trainer is None:
            self.initialize()
        
        try:
            model_path = model_path or settings.model_save_path
            
            if not Path(model_path).exists():
                logger.warning(f"Model not found at {model_path}, will train new model")
                return False, f"Model not found at {model_path}"
            
            self.trainer.load_model(model_path)
            self.model_loaded = True
            self.model_info = {
                "model_type": "loaded",
                "trained": True,
                "loaded_date": datetime.now().isoformat(),
                "path": model_path
            }
            
            logger.info(f"Model loaded from {model_path}")
            return True, f"Model loaded from {model_path}"
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False, str(e)
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict sentiment for text
        
        Args:
            text: Text to analyze
            
        Returns:
            Prediction result dictionary
        """
        if not self.model_loaded:
            # Try to load model
            success, message = self.load_model()
            if not success:
                # Try to train model
                success, train_results = self.train()
                if not success:
                    raise RuntimeError("Model not loaded and training failed")
        
        try:
            prediction = self.trainer.predict(text)
            return prediction
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def batch_predict(self, texts: list) -> list:
        """
        Predict sentiment for multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of prediction results
        """
        predictions = []
        for text in texts:
            try:
                prediction = self.predict(text)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Prediction failed for text: {text[:50]}... - {e}")
                predictions.append({
                    "text": text,
                    "error": str(e)
                })
        
        return predictions
    
    def evaluate(
        self,
        test_path: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate model on test data
        
        Args:
            test_path: Path to test data (uses default if None)
            
        Returns:
            Tuple of (success, evaluation results)
        """
        if not self.model_loaded:
            success, message = self.load_model()
            if not success:
                return False, {"error": message}
        
        try:
            test_path = test_path or settings.test_data_path
            
            eval_results = self.trainer.evaluate(test_path)
            
            # Update model info
            if "accuracy" in eval_results:
                self.model_info["test_accuracy"] = eval_results["accuracy"]
                self.model_info["test_f1"] = eval_results["f1_score"]
            
            return True, eval_results
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return False, {"error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return self.model_info
    
    def get_training_history(self) -> list:
        """Get training history"""
        return self.training_history
    
    def shutdown(self) -> None:
        """Cleanup resources"""
        if self.trainer:
            self.trainer.stop()
            self.trainer = None
        self.model_loaded = False
        logger.info("Model manager shutdown")


# Global model manager instance
model_manager = SentimentModelManager()
