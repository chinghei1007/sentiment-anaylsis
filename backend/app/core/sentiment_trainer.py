"""
PySpark Sentiment Analysis Trainer
Trains classification models on user comments for positive/negative sentiment
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    HashingTF, 
    IDF, 
    Tokenizer, 
    StopWordsRemover,
    StringIndexer,
    VectorAssembler
)
from pyspark.ml.classification import (
    LogisticRegression,
    NaiveBayes,
    RandomForestClassifier,
    GBTClassifier
)
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import col, when
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from app.core.dataset_parser import UnifiedDatasetLoader, DatasetParserFactory


class SentimentTrainer:
    """
    PySpark-based sentiment analysis model trainer
    Focuses on user comments with positive/negative classification
    """
    
    def __init__(self, app_name: str = "SentimentAnalysis"):
        """
        Initialize Spark session and trainer
        
        Args:
            app_name: Name for the Spark application
        """
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.repl.eagerEval.enabled", True) \
            .getOrCreate()
        
        self.model = None
        self.pipeline = None
        self.label_indexer = None
        self.feature_columns = []
        self.label_column = "label"
        self.text_column = "text"
        self.output_column = "prediction"
        
    def load_dataset(
        self, 
        data_path: str,
        format: str = "csv",
        text_col: str = "text",
        sentiment_col: str = "sentiment"
    ) -> Tuple:
        """
        Load dataset from file
        
        Args:
            data_path: Path to the dataset file
            format: File format (csv, json, txt)
            text_col: Column name for text/comments
            sentiment_col: Column name for sentiment labels
            
        Returns:
            Tuple of (DataFrame, label counts dict)
        """
        if format == "csv":
            df = self.spark.read.csv(
                data_path, 
                header=True, 
                inferSchema=True,
                comment="#"
            )
        elif format == "json":
            df = self.spark.read.json(data_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Filter for only positive and negative (remove neutral)
        df = df.filter(col(sentiment_col).isin(["positive", "negative"]))
        
        # Convert sentiment to binary label
        df = df.withColumn(
            self.label_column,
            when(col(sentiment_col) == "positive", 1.0)
                .when(col(sentiment_col) == "negative", 0.0)
                .otherwise(None)
        )
        
        # Select relevant columns
        df = df.select(
            col("id").cast(IntegerType()),
            col(text_col).alias(self.text_column),
            col(self.label_column),
            col(sentiment_col),
            col("source"),
            col("date")
        )
        
        # Get label distribution
        label_counts = df.groupBy(self.label_column).count().collect()
        label_dist = {row[self.label_column]: row["count"] for row in label_counts}
        
        return df, label_dist
    
    def preprocess_text(self, df) -> Tuple:
        """
        Create text preprocessing pipeline
        
        Args:
            df: Input DataFrame with text column
            
        Returns:
            Tuple of (preprocessed DataFrame, pipeline stages)
        """
        # Tokenizer
        tokenizer = Tokenizer(
            inputCol=self.text_column,
            outputCol="words"
        )
        
        # Stop words remover
        stop_words = StopWordsRemover.loadDefaultStopWords("english")
        remover = StopWordsRemover(
            inputCol="words",
            outputCol="filtered_words",
            stopWords=stop_words
        )
        
        # HashingTF for feature extraction
        hashing_tf = HashingTF(
            inputCol="filtered_words",
            outputCol="raw_features",
            numFeatures=20000
        )
        
        # IDF for weighting
        idf = IDF(
            inputCol="raw_features",
            outputCol="features"
        )
        
        # String indexer for labels
        self.label_indexer = StringIndexer(
            inputCol=self.label_column,
            outputCol="label_index"
        )
        
        return tokenizer, remover, hashing_tf, idf
    
    def create_pipeline(self, model_type: str = "logistic") -> Pipeline:
        """
        Create ML pipeline with selected classifier
        
        Args:
            model_type: Type of classifier (logistic, naive_bayes, random_forest, gbt)
            
        Returns:
            Pipeline object
        """
        tokenizer, remover, hashing_tf, idf = self.preprocess_text(self.spark.createDataFrame([], "string"))
        
        # Select classifier
        if model_type == "logistic":
            classifier = LogisticRegression(
                featuresCol="features",
                labelCol="label_index",
                maxIter=100,
                regParam=0.01
            )
        elif model_type == "naive_bayes":
            classifier = NaiveBayes(
                featuresCol="features",
                labelCol="label_index",
                smoothing=1.0
            )
        elif model_type == "random_forest":
            classifier = RandomForestClassifier(
                featuresCol="features",
                labelCol="label_index",
                numTrees=100,
                maxDepth=5
            )
        elif model_type == "gbt":
            classifier = GBTClassifier(
                featuresCol="features",
                labelCol="label_index",
                maxIter=100,
                maxDepth=5
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Create pipeline
        pipeline = Pipeline(stages=[
            tokenizer,
            remover,
            hashing_tf,
            idf,
            self.label_indexer,
            classifier
        ])
        
        return pipeline
    
    def train(
        self,
        train_data_path: str,
        model_type: str = "logistic",
        validation_split: float = 0.2,
        random_seed: int = 42
    ) -> Dict[str, Any]:
        """
        Train sentiment analysis model
        
        Args:
            train_data_path: Path to training data
            model_type: Type of classifier to use
            validation_split: Fraction of data to use for validation
            random_seed: Random seed for reproducibility
            
        Returns:
            Dictionary with training results and metrics
        """
        # Load data
        df, label_dist = self.load_dataset(train_data_path)
        
        # Split into train and validation
        train_df, val_df = df.randomSplit(
            [1.0 - validation_split, validation_split],
            seed=random_seed
        )
        
        # Create and fit pipeline
        self.pipeline = self.create_pipeline(model_type)
        self.model = self.pipeline.fit(train_df)
        
        # Predict on validation set
        val_predictions = self.model.transform(val_df)
        
        # Evaluate
        evaluator = MulticlassClassificationEvaluator(
            labelCol="label_index",
            predictionCol="prediction",
            metricName="accuracy"
        )
        
        accuracy = evaluator.evaluate(val_predictions)
        
        # Calculate additional metrics
        val_predictions.createOrReplaceTempView("validation_predictions")
        
        # Confusion matrix
        confusion = self.spark.sql("""
            SELECT 
                label_index as true_label,
                prediction as pred_label,
                COUNT(*) as count
            FROM validation_predictions
            GROUP BY label_index, prediction
            ORDER BY label_index, prediction
        """).collect()
        
        # Create confusion matrix dict
        cm = {}
        for row in confusion:
            true = int(row.true_label)
            pred = int(row.pred_label)
            if true not in cm:
                cm[true] = {}
            cm[true][pred] = int(row.count)
        
        # Collect predictions for detailed analysis
        predictions_list = val_predictions.select(
            self.text_column,
            self.label_column,
            "prediction"
        ).collect()
        
        sample_predictions = []
        for row in predictions_list[:10]:
            sample_predictions.append({
                "text": row[self.text_column],
                "true_label": int(row[self.label_column]),
                "predicted": int(row["prediction"])
            })
        
        return {
            "model_type": model_type,
            "training_samples": train_df.count(),
            "validation_samples": val_df.count(),
            "label_distribution": label_dist,
            "accuracy": float(accuracy),
            "confusion_matrix": cm,
            "sample_predictions": sample_predictions,
            "timestamp": datetime.now().isoformat()
        }
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict sentiment for a single text
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with prediction and confidence
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Create DataFrame from text
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField(self.text_column, StringType(), True),
            StructField(self.label_column, DoubleType(), True),
            StructField("sentiment", StringType(), True),
            StructField("source", StringType(), True),
            StructField("date", StringType(), True)
        ])
        
        # Dummy values for required columns
        data = [(0, text, 0.0, "unknown", "unknown", "unknown")]
        df = self.spark.createDataFrame(data, schema)
        
        # Predict
        predictions = self.model.transform(df)
        prediction = predictions.select("prediction").collect()[0][0]
        
        # Get probabilities if available (for LogisticRegression)
        if hasattr(self.pipeline.stages[-1], "predictRaw"):
            raw_predictions = self.model.stages[-1].predictRaw(
                predictions.select("features").collect()[0][0]
            )
            prob_positive = float(raw_predictions[1])
            prob_negative = float(raw_predictions[0])
            confidence = max(prob_positive, prob_negative)
        else:
            prob_positive = None
            prob_negative = None
            confidence = None
        
        sentiment = "positive" if prediction == 1.0 else "negative"
        
        return {
            "text": text,
            "sentiment": sentiment,
            "label": int(prediction),
            "confidence": confidence,
            "prob_positive": prob_positive,
            "prob_negative": prob_negative
        }
    
    def evaluate(self, test_data_path: str) -> Dict[str, Any]:
        """
        Evaluate trained model on test data
        
        Args:
            test_data_path: Path to test data
            
        Returns:
            Dictionary with evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Load test data
        test_df, _ = self.load_dataset(test_data_path)
        
        # Predict
        predictions = self.model.transform(test_df)
        
        # Evaluate
        evaluator = MulticlassClassificationEvaluator(
            labelCol="label_index",
            predictionCol="prediction"
        )
        
        accuracy = evaluator.evaluate(predictions)
        
        # F1 score
        f1 = evaluator.setMetricName("f1").evaluate(predictions)
        
        # Weighted precision
        precision = evaluator.setMetricName("weightedPrecision").evaluate(predictions)
        
        # Weighted recall
        recall = evaluator.setMetricName("weightedRecall").evaluate(predictions)
        
        # Confusion matrix
        predictions.createOrReplaceTempView("test_predictions")
        confusion = self.spark.sql("""
            SELECT 
                label_index as true_label,
                prediction as pred_label,
                COUNT(*) as count
            FROM test_predictions
            GROUP BY label_index, prediction
            ORDER BY label_index, prediction
        """).collect()
        
        cm = {}
        for row in confusion:
            true = int(row.true_label)
            pred = int(row.pred_label)
            if true not in cm:
                cm[true] = {}
            cm[true][pred] = int(row.count)
        
        return {
            "accuracy": float(accuracy),
            "f1_score": float(f1),
            "precision": float(precision),
            "recall": float(recall),
            "confusion_matrix": cm,
            "total_samples": test_df.count(),
            "positive_samples": int(test_df.filter(col(self.label_column) == 1.0).count()),
            "negative_samples": int(test_df.filter(col(self.label_column) == 0.0).count())
        }
    
    def save_model(self, model_path: str) -> None:
        """
        Save trained model to disk
        
        Args:
            model_path: Directory to save model
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        self.model.write().overwrite().save(model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str) -> None:
        """
        Load trained model from disk
        
        Args:
            model_path: Directory where model is saved
        """
        from pyspark.ml import PipelineModel
        
        self.model = PipelineModel.load(model_path)
        print(f"Model loaded from {model_path}")
    
    def stop(self) -> None:
        """Stop Spark session"""
        self.spark.stop()
        print("Spark session stopped")


def train_sentiment_model(
    train_path: str,
    test_path: str,
    model_type: str = "logistic",
    model_save_path: Optional[str] = None
) -> Tuple[SentimentTrainer, Dict[str, Any]]:
    """
    Convenience function to train and evaluate a sentiment model
    
    Args:
        train_path: Path to training data
        test_path: Path to test data
        model_type: Type of classifier
        model_save_path: Optional path to save model
        
    Returns:
        Tuple of (trained trainer, evaluation results)
    """
    trainer = SentimentTrainer()
    
    # Train
    train_results = trainer.train(train_path, model_type=model_type)
    print(f"Training completed. Accuracy: {train_results['accuracy']:.4f}")
    
    # Evaluate on test set
    eval_results = trainer.evaluate(test_path)
    print(f"Test evaluation: Accuracy={eval_results['accuracy']:.4f}, "
          f"F1={eval_results['f1_score']:.4f}")
    
    # Save model if requested
    if model_save_path:
        trainer.save_model(model_save_path)
    
    return trainer, eval_results


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    # Paths to data (using the cloned dataset)
    base_path = Path("/workspace/github__rskworld__sentiment-analysis/data")
    train_path = str(base_path / "train_data.csv")
    test_path = str(base_path / "test_data.csv")
    
    print("Starting sentiment analysis training...")
    print(f"Training data: {train_path}")
    print(f"Test data: {test_path}")
    
    # Train model
    trainer, results = train_sentiment_model(
        train_path=train_path,
        test_path=test_path,
        model_type="logistic",
        model_save_path="/workspace/sentiment-analysis-app/models/sentiment_model"
    )
    
    # Test predictions
    test_texts = [
        "I absolutely love this product! It's amazing!",
        "This is the worst experience ever. Terrible quality.",
        "It's okay, nothing special."
    ]
    
    for text in test_texts:
        try:
            prediction = trainer.predict(text)
            print(f"\nText: {text}")
            print(f"Sentiment: {prediction['sentiment']}")
            print(f"Label: {prediction['label']}")
        except Exception as e:
            print(f"Error predicting: {e}")
    
    # Stop Spark
    trainer.stop()
