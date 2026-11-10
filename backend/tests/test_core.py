"""
Unit Tests for Core Components (No Server Required)
"""

import pytest
from pathlib import Path
from datetime import datetime

# Test imports
from app.core.config import settings
from app.core.dataset_parser import (
    CSVParser,
    JSONParser,
    TSVParser,
    DatasetParserFactory,
    UnifiedDatasetLoader
)
from app.utils.helpers import (
    sanitize_text,
    validate_sentiment_label,
    convert_label_to_numeric,
    get_file_extension
)


# Configuration Tests
class TestConfig:
    def test_settings_initialization(self):
        """Test configuration settings"""
        assert settings.app_name == "Sentiment Analysis API"
        assert settings.app_version == "1.0.0"
        assert settings.debug is True
        assert len(settings.cors_origins) > 0

    def test_data_dir_exists(self):
        """Test data directory path"""
        assert Path(settings.data_dir).exists() or settings.data_dir.name == "sentiment-analysis"


# Helper Function Tests
class TestHelpers:
    def test_sanitize_text_empty(self):
        """Test sanitizing empty text"""
        assert sanitize_text("") == ""

    def test_sanitize_text_whitespace(self):
        """Test sanitizing text with excessive whitespace"""
        result = sanitize_text("  hello   world  ")
        assert result == "hello world"

    def test_sanitize_text_long(self):
        """Test sanitizing very long text"""
        long_text = "a" * 20000
        result = sanitize_text(long_text, max_length=100)
        assert len(result) <= 100

    def test_validate_sentiment_label_positive(self):
        """Test validating positive label"""
        assert validate_sentiment_label("positive") == "positive"
        assert validate_sentiment_label("POSITIVE") == "positive"
        assert validate_sentiment_label("pos") == "positive"
        assert validate_sentiment_label("1") == "positive"

    def test_validate_sentiment_label_negative(self):
        """Test validating negative label"""
        assert validate_sentiment_label("negative") == "negative"
        assert validate_sentiment_label("NEGATIVE") == "negative"
        assert validate_sentiment_label("neg") == "negative"
        assert validate_sentiment_label("0") == "negative"

    def test_validate_sentiment_label_neutral(self):
        """Test validating neutral label"""
        assert validate_sentiment_label("neutral") == "neutral"
        assert validate_sentiment_label("unknown") == "neutral"

    def test_convert_label_to_numeric(self):
        """Test converting label to numeric"""
        assert convert_label_to_numeric("positive") == 1.0
        assert convert_label_to_numeric("negative") == 0.0
        assert convert_label_to_numeric("neutral") is None

    def test_get_file_extension(self):
        """Test getting file extension"""
        assert get_file_extension("data.csv") == "csv"
        assert get_file_extension("data.json") == "json"
        assert get_file_extension("data.tsv") == "tsv"
        assert get_file_extension("data.txt") == "txt"
        assert get_file_extension("/path/to/data.csv") == "csv"


# Dataset Parser Tests
class TestDatasetParsers:
    @pytest.fixture
    def spark_session(self):
        """Create Spark session for testing"""
        from pyspark.sql import SparkSession
        return SparkSession.builder \
            .appName("TestParser") \
            .config("spark.sql.repl.eagerEval.enabled", True) \
            .getOrCreate()

    @pytest.fixture
    def sample_csv_path(self):
        """Create sample CSV file for testing"""
        import tempfile
        import os
        
        csv_content = """id,text,sentiment,source
1,"Great product",positive,Product Review
2,"Terrible quality",negative,Customer Feedback
3,"Okay experience",neutral,Social Media
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            yield f.name
        
        os.unlink(f.name)

    def test_csv_parser_initialization(self):
        """Test CSV parser initialization"""
        parser = CSVParser(
            text_column="text",
            label_column="sentiment"
        )
        assert parser.text_column == "text"
        assert parser.label_column == "sentiment"

    def test_csv_parser_metadata(self):
        """Test CSV parser metadata"""
        parser = CSVParser()
        metadata = parser.get_metadata()
        assert metadata["type"] == "csv"

    def test_tsv_parser_metadata(self):
        """Test TSV parser metadata"""
        parser = TSVParser()
        metadata = parser.get_metadata()
        assert metadata["type"] == "tsv"

    def test_parser_factory_get_parser(self):
        """Test parser factory"""
        csv_parser = DatasetParserFactory.get_parser("csv")
        assert isinstance(csv_parser, CSVParser)
        
        json_parser = DatasetParserFactory.get_parser("json")
        assert isinstance(json_parser, JSONParser)

    def test_parser_factory_auto_detect(self, sample_csv_path):
        """Test auto-detection of parser"""
        parser = DatasetParserFactory.auto_detect(sample_csv_path)
        assert isinstance(parser, CSVParser)

    def test_unified_loader(self, spark_session, sample_csv_path):
        """Test unified dataset loader"""
        loader = UnifiedDatasetLoader(spark_session)
        df, metadata = loader.load(sample_csv_path)
        
        assert df is not None
        assert df.count() == 3
        assert "text" in df.columns
        assert "sentiment" in df.columns
        assert metadata["parser"] == "CSVParser"


# Configuration Tests
class TestEnvironment:
    def test_python_version(self):
        """Test Python version"""
        import sys
        assert sys.version_info >= (3, 8)

    def test_pyspark_available(self):
        """Test PySpark availability"""
        try:
            import pyspark
            assert pyspark.__version__ >= "3.0.0"
        except ImportError:
            pytest.fail("PySpark not installed")

    def test_fastapi_available(self):
        """Test FastAPI availability"""
        try:
            import fastapi
            assert fastapi.__version__ >= "0.100.0"
        except ImportError:
            pytest.fail("FastAPI not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
