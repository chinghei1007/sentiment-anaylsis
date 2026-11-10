"""
Flexible Dataset Parser System
Handles different dataset formats and column structures from various sources
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, when, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class DatasetParser(ABC):
    """Abstract base class for dataset parsers"""
    
    @abstractmethod
    def parse(self, data_path: str, spark: SparkSession) -> Tuple[DataFrame, Dict[str, Any]]:
        """
        Parse dataset from file
        
        Args:
            data_path: Path to dataset file
            spark: SparkSession instance
            
        Returns:
            Tuple of (DataFrame, metadata dict)
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get parser metadata"""
        pass


class CSVParser(DatasetParser):
    """Parser for CSV datasets with configurable columns"""
    
    def __init__(
        self,
        text_column: str = "text",
        label_column: str = "sentiment",
        delimiter: str = ",",
        header: bool = True,
        quote_char: str = '"',
        escape_char: str = "\\",
        comment: str = "#"
    ):
        """
        Initialize CSV parser
        
        Args:
            text_column: Column name for text/content
            label_column: Column name for sentiment label
            delimiter: CSV delimiter
            header: Whether file has header
            quote_char: Quote character
            escape_char: Escape character
            comment: Comment character for lines to skip
        """
        self.text_column = text_column
        self.label_column = label_column
        self.delimiter = delimiter
        self.header = header
        self.quote_char = quote_char
        self.escape_char = escape_char
        self.comment = comment
        
    def parse(self, data_path: str, spark: SparkSession) -> Tuple[DataFrame, Dict[str, Any]]:
        """Parse CSV file"""
        try:
            df = spark.read.csv(
                data_path,
                header=self.header,
                sep=self.delimiter,
                quote=self.quote_char,
                escape=self.escape_char,
                comment=self.comment,
                inferSchema=True,
                multiLine=True
            )
            
            # Ensure required columns exist
            if self.text_column not in df.columns:
                raise ValueError(f"Text column '{self.text_column}' not found in CSV")
            if self.label_column not in df.columns:
                raise ValueError(f"Label column '{self.label_column}' not found in CSV")
            
            # Standardize column names
            df = df.withColumnRenamed(self.text_column, "text")
            df = df.withColumnRenamed(self.label_column, "raw_sentiment")
            
            # Normalize sentiment labels
            df = df.withColumn(
                "sentiment",
                when(col("raw_sentiment").isin(["positive", "pos", "1", "good", "great"]), "positive")
                .when(col("raw_sentiment").isin(["negative", "neg", "0", "bad", "poor"]), "negative")
                .when(col("raw_sentiment").isin(["neutral", "0.5", "avg", "average"]), "neutral")
                .otherwise(col("raw_sentiment"))
            )
            
            # Add source
            df = df.withColumn("source", lit(Path(data_path).name))
            
            # Add ID if not present
            if "id" not in df.columns:
                from pyspark.sql.functions import monotonically_increasing_id
                df = df.withColumn("id", monotonically_increasing_id().cast(IntegerType()))
            
            # Select standard columns
            standard_cols = ["id", "text", "sentiment", "source"]
            available_cols = [c for c in df.columns if c in standard_cols or c not in ["raw_sentiment"]]
            df = df.select(*available_cols)
            
            metadata = {
                "parser": "CSVParser",
                "text_column": self.text_column,
                "label_column": self.label_column,
                "row_count": df.count(),
                "columns": df.columns
            }
            
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error parsing CSV {data_path}: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get parser configuration"""
        return {
            "type": "csv",
            "text_column": self.text_column,
            "label_column": self.label_column,
            "delimiter": self.delimiter,
            "header": self.header
        }


class JSONParser(DatasetParser):
    """Parser for JSON datasets"""
    
    def __init__(
        self,
        text_column: str = "text",
        label_column: str = "sentiment",
        multi_line: bool = True
    ):
        """
        Initialize JSON parser
        
        Args:
            text_column: Column name for text
            label_column: Column name for sentiment
            multi_line: Whether JSON is multi-line
        """
        self.text_column = text_column
        self.label_column = label_column
        self.multi_line = multi_line
        
    def parse(self, data_path: str, spark: SparkSession) -> Tuple[DataFrame, Dict[str, Any]]:
        """Parse JSON file"""
        try:
            df = spark.read.json(
                data_path,
                multiLine=self.multi_line
            )
            
            # Handle nested JSON
            if self.text_column not in df.columns:
                # Try to find nested text column
                for col_name in df.columns:
                    if df.schema[col_name].dataType.typeName() == "struct":
                        nested_df = df.select(f"{col_name}.*")
                        if self.text_column in nested_df.columns:
                            df = nested_df
                            break
            
            # Ensure required columns exist
            if self.text_column not in df.columns:
                raise ValueError(f"Text column '{self.text_column}' not found in JSON")
            if self.label_column not in df.columns:
                raise ValueError(f"Label column '{self.label_column}' not found in JSON")
            
            # Standardize
            df = df.withColumnRenamed(self.text_column, "text")
            df = df.withColumnRenamed(self.label_column, "raw_sentiment")
            
            # Normalize sentiment
            df = df.withColumn(
                "sentiment",
                when(col("raw_sentiment").isin(["positive", "pos", "1"]), "positive")
                .when(col("raw_sentiment").isin(["negative", "neg", "0"]), "negative")
                .otherwise("neutral")
            )
            
            # Add source
            df = df.withColumn("source", lit(Path(data_path).name))
            
            # Add ID
            if "id" not in df.columns:
                from pyspark.sql.functions import monotonically_increasing_id
                df = df.withColumn("id", monotonically_increasing_id().cast(IntegerType()))
            
            metadata = {
                "parser": "JSONParser",
                "text_column": self.text_column,
                "label_column": self.label_column,
                "row_count": df.count(),
                "columns": df.columns
            }
            
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error parsing JSON {data_path}: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "json",
            "text_column": self.text_column,
            "label_column": self.label_column,
            "multi_line": self.multi_line
        }


class TSVParser(CSVParser):
    """Parser for TSV (tab-separated) datasets"""
    
    def __init__(
        self,
        text_column: str = "text",
        label_column: str = "sentiment"
    ):
        super().__init__(
            text_column=text_column,
            label_column=label_column,
            delimiter="\t"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        metadata = super().get_metadata()
        metadata["type"] = "tsv"
        return metadata


class AmazonReviewParser(DatasetParser):
    """Parser for Amazon review datasets (common Kaggle format)"""
    
    def __init__(self):
        """Initialize Amazon review parser"""
        pass
    
    def parse(self, data_path: str, spark: SparkSession) -> Tuple[DataFrame, Dict[str, Any]]:
        """Parse Amazon review dataset"""
        try:
            # Amazon reviews typically have columns like:
            # - reviewText or Text
            # - Score (1-5 stars)
            df = spark.read.csv(
                data_path,
                header=True,
                inferSchema=True,
                multiLine=True
            )
            
            # Find text column
            text_col = None
            for col_name in ["reviewText", "Text", "content", "text"]:
                if col_name in df.columns:
                    text_col = col_name
                    break
            
            if not text_col:
                raise ValueError("No text column found in Amazon review dataset")
            
            # Find score column
            score_col = None
            for col_name in ["Score", "score", "rating", "Rating"]:
                if col_name in df.columns:
                    score_col = col_name
                    break
            
            if not score_col:
                raise ValueError("No score column found in Amazon review dataset")
            
            # Convert score to sentiment
            df = df.withColumn(
                "sentiment",
                when(col(score_col) >= 4, "positive")
                .when(col(score_col) <= 2, "negative")
                .otherwise("neutral")
            )
            
            # Standardize
            df = df.withColumnRenamed(text_col, "text")
            df = df.withColumn("source", lit("Amazon Review"))
            
            # Add ID
            if "id" not in df.columns:
                from pyspark.sql.functions import monotonically_increasing_id
                df = df.withColumn("id", monotonically_increasing_id().cast(IntegerType()))
            
            # Select standard columns
            standard_cols = ["id", "text", "sentiment", "source"]
            available_cols = [c for c in df.columns if c in standard_cols]
            df = df.select(*available_cols)
            
            metadata = {
                "parser": "AmazonReviewParser",
                "text_column": text_col,
                "score_column": score_col,
                "row_count": df.count(),
                "columns": df.columns
            }
            
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error parsing Amazon review {data_path}: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "amazon_review",
            "description": "Amazon product review dataset"
        }


class TwitterParser(DatasetParser):
    """Parser for Twitter/social media datasets"""
    
    def __init__(self):
        """Initialize Twitter parser"""
        pass
    
    def parse(self, data_path: str, spark: SparkSession) -> Tuple[DataFrame, Dict[str, Any]]:
        """Parse Twitter dataset"""
        try:
            df = spark.read.csv(
                data_path,
                header=True,
                inferSchema=True,
                multiLine=True
            )
            
            # Twitter datasets typically have:
            # - text, tweet, content
            # - sentiment, label, target
            text_col = None
            for col_name in ["text", "tweet", "content", "Text"]:
                if col_name in df.columns:
                    text_col = col_name
                    break
            
            if not text_col:
                raise ValueError("No text column found in Twitter dataset")
            
            label_col = None
            for col_name in ["sentiment", "label", "target", "Sentiment"]:
                if col_name in df.columns:
                    label_col = col_name
                    break
            
            if not label_col:
                raise ValueError("No sentiment column found in Twitter dataset")
            
            # Standardize
            df = df.withColumnRenamed(text_col, "text")
            df = df.withColumnRenamed(label_col, "raw_sentiment")
            
            # Normalize sentiment
            df = df.withColumn(
                "sentiment",
                when(col("raw_sentiment").isin(["positive", "pos", "1", "4"]), "positive")
                .when(col("raw_sentiment").isin(["negative", "neg", "0", "-1", "0"]), "negative")
                .otherwise("neutral")
            )
            
            df = df.withColumn("source", lit("Twitter"))
            
            # Add ID
            if "id" not in df.columns:
                from pyspark.sql.functions import monotonically_increasing_id
                df = df.withColumn("id", monotonically_increasing_id().cast(IntegerType()))
            
            # Select standard columns
            standard_cols = ["id", "text", "sentiment", "source"]
            available_cols = [c for c in df.columns if c in standard_cols]
            df = df.select(*available_cols)
            
            metadata = {
                "parser": "TwitterParser",
                "text_column": text_col,
                "label_column": label_col,
                "row_count": df.count(),
                "columns": df.columns
            }
            
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error parsing Twitter dataset {data_path}: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "twitter",
            "description": "Twitter/social media dataset"
        }


class DatasetParserFactory:
    """Factory for creating dataset parsers"""
    
    PARSERS: Dict[str, DatasetParser] = {
        "csv": CSVParser(),
        "json": JSONParser(),
        "tsv": TSVParser(),
        "amazon": AmazonReviewParser(),
        "twitter": TwitterParser()
    }
    
    @classmethod
    def get_parser(cls, parser_type: str, **kwargs) -> DatasetParser:
        """
        Get parser by type
        
        Args:
            parser_type: Type of parser (csv, json, tsv, amazon, twitter)
            **kwargs: Parser-specific arguments
            
        Returns:
            DatasetParser instance
        """
        parser_type = parser_type.lower()
        
        if parser_type in cls.PARSERS:
            return cls.PARSERS[parser_type]
        
        # Create new parser based on type
        if parser_type == "csv":
            return CSVParser(**kwargs)
        elif parser_type == "json":
            return JSONParser(**kwargs)
        elif parser_type == "tsv":
            return TSVParser(**kwargs)
        elif parser_type == "amazon":
            return AmazonReviewParser()
        elif parser_type == "twitter":
            return TwitterParser()
        else:
            # Default to CSV parser
            logger.warning(f"Unknown parser type '{parser_type}', using CSV parser")
            return CSVParser(**kwargs)
    
    @classmethod
    def auto_detect(cls, data_path: str, **kwargs) -> DatasetParser:
        """
        Auto-detect parser based on file extension
        
        Args:
            data_path: Path to dataset file
            **kwargs: Parser-specific arguments
            
        Returns:
            Appropriate DatasetParser instance
        """
        ext = Path(data_path).suffix.lower()
        
        if ext == ".csv":
            return cls.get_parser("csv", **kwargs)
        elif ext == ".json":
            return cls.get_parser("json", **kwargs)
        elif ext == ".tsv" or ext == ".txt":
            return cls.get_parser("tsv", **kwargs)
        else:
            # Try CSV first
            return cls.get_parser("csv", **kwargs)


class UnifiedDatasetLoader:
    """
    Unified loader that can handle multiple dataset formats
    """
    
    def __init__(self, spark: SparkSession):
        """
        Initialize dataset loader
        
        Args:
            spark: SparkSession instance
        """
        self.spark = spark
        self.parsers: Dict[str, DatasetParser] = {}
        
    def load(
        self,
        data_path: str,
        parser_type: Optional[str] = None,
        **parser_kwargs
    ) -> Tuple[DataFrame, Dict[str, Any]]:
        """
        Load dataset using appropriate parser
        
        Args:
            data_path: Path to dataset file
            parser_type: Type of parser to use (auto-detected if None)
            **parser_kwargs: Arguments for parser
            
        Returns:
            Tuple of (DataFrame, metadata)
        """
        if parser_type:
            parser = DatasetParserFactory.get_parser(parser_type, **parser_kwargs)
        else:
            parser = DatasetParserFactory.auto_detect(data_path, **parser_kwargs)
        
        df, metadata = parser.parse(data_path, self.spark)
        
        # Add parser info to metadata
        metadata["parser_info"] = parser.get_metadata()
        metadata["file_path"] = data_path
        
        return df, metadata
    
    def load_multiple(
        self,
        data_paths: List[str],
        parser_type: Optional[str] = None,
        **parser_kwargs
    ) -> Tuple[DataFrame, List[Dict[str, Any]]]:
        """
        Load multiple datasets and combine
        
        Args:
            data_paths: List of dataset paths
            parser_type: Parser type (auto-detected if None)
            **parser_kwargs: Parser arguments
            
        Returns:
            Tuple of (combined DataFrame, list of metadata)
        """
        all_dfs = []
        all_metadata = []
        
        for data_path in data_paths:
            df, metadata = self.load(data_path, parser_type, **parser_kwargs)
            all_dfs.append(df)
            all_metadata.append(metadata)
        
        # Union all DataFrames
        combined_df = all_dfs[0]
        for df in all_dfs[1:]:
            combined_df = combined_df.unionByName(df)
        
        return combined_df, all_metadata


# Example usage
if __name__ == "__main__":
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder \
        .appName("DatasetParserTest") \
        .getOrCreate()
    
    # Test with the cloned dataset
    loader = UnifiedDatasetLoader(spark)
    
    data_path = "/workspace/github__rskworld__sentiment-analysis/data/sentiment_data.csv"
    
    # Load with auto-detection
    df, metadata = loader.load(data_path)
    
    print(f"Loaded {df.count()} rows")
    print(f"Columns: {df.columns}")
    print(f"Metadata: {metadata}")
    
    # Show sample
    df.show(5)
    
    spark.stop()
