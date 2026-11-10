"""
Spark-specific utility functions
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col
import logging

logger = logging.getLogger(__name__)


def get_spark_session(app_name: str = "SentimentAnalysis") -> SparkSession:
    """
    Get or create Spark session
    
    Args:
        app_name: Name for the Spark application
        
    Returns:
        SparkSession instance
    """
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.repl.eagerEval.enabled", True) \
        .getOrCreate()


def check_spark_available() -> bool:
    """Check if Spark is available"""
    try:
        spark = get_spark_session()
        spark.stop()
        return True
    except Exception as e:
        logger.error(f"Spark not available: {e}")
        return False


def get_dataframe_info(df: DataFrame) -> dict:
    """Get information about a Spark DataFrame"""
    return {
        "row_count": df.count(),
        "columns": [field.name for field in df.schema.fields],
        "schema": str(df.schema)
    }


def filter_dataframe_by_column(
    df: DataFrame,
    column: str,
    values: list
) -> DataFrame:
    """Filter DataFrame by column values"""
    return df.filter(col(column).isin(values))


def sample_dataframe(df: DataFrame, fraction: float = 0.1, seed: int = 42) -> DataFrame:
    """Sample a DataFrame"""
    return df.sample(fraction=fraction, seed=seed)
