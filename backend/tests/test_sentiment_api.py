"""
End-to-End Tests for Sentiment Analysis API
"""

import pytest
import httpx
import asyncio
from datetime import datetime
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

# Fixtures
@pytest.fixture(scope="session")
def api_client():
    """Create HTTP client for API tests"""
    return httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT)

@pytest.fixture(scope="session", autouse=True)
async def setup_and_teardown(api_client):
    """Setup and teardown for test session"""
    # Start the FastAPI server before tests
    # Note: In production, use pytest-asyncio with async server lifecycle
    yield
    # Cleanup after tests
    await api_client.aclose()


# Test Data
class TestData:
    POSITIVE_TEXT = "I love this product! It is absolutely amazing and excellent quality."
    NEGATIVE_TEXT = "This is terrible. Worst experience ever. Poor quality and bad service."
    NEUTRAL_TEXT = "This is okay. Nothing special but not bad either."
    LONG_TEXT = "The product I purchased last week has been working perfectly. " + \
                "The quality is outstanding and the customer service was excellent. " + \
                "I would definitely recommend this to all my friends and family. " + \
                "It exceeded all my expectations and I am very satisfied with my purchase."
    
    BATCH_TEXTs = [
        "Great product!",
        "Terrible quality",
        "Okay experience",
        "Excellent service",
        "Worst purchase ever"
    ]


# Health Check Tests
class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_endpoint(self, api_client):
        """Test API health endpoint"""
        response = await api_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "spark_available" in data
        assert "model_loaded" in data

    @pytest.mark.asyncio
    async def test_health_spark_available(self, api_client):
        """Test Spark availability in health check"""
        response = await api_client.get("/api/v1/health")
        data = response.json()
        assert data["spark_available"] is True


# Sentiment Prediction Tests
class TestSentimentPrediction:
    @pytest.mark.asyncio
    async def test_predict_positive(self, api_client):
        """Test prediction of positive sentiment"""
        response = await api_client.post(
            "/api/v1/predict",
            json={"text": TestData.POSITIVE_TEXT}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "positive"
        assert data["label"] == 1
        assert "confidence" in data
        assert data["text"] == TestData.POSITIVE_TEXT

    @pytest.mark.asyncio
    async def test_predict_negative(self, api_client):
        """Test prediction of negative sentiment"""
        response = await api_client.post(
            "/api/v1/predict",
            json={"text": TestData.NEGATIVE_TEXT}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "negative"
        assert data["label"] == 0
        assert "confidence" in data

    @pytest.mark.asyncio
    async def test_predict_with_probabilities(self, api_client):
        """Test prediction returns probabilities"""
        response = await api_client.post(
            "/api/v1/predict",
            json={"text": TestData.POSITIVE_TEXT}
        )
        assert response.status_code == 200
        data = response.json()
        assert "prob_positive" in data
        assert "prob_negative" in data
        assert 0 <= data["prob_positive"] <= 1
        assert 0 <= data["prob_negative"] <= 1

    @pytest.mark.asyncio
    async def test_predict_empty_text(self, api_client):
        """Test prediction with empty text"""
        response = await api_client.post(
            "/api/v1/predict",
            json={"text": ""}
        )
        # Should return error or handle gracefully
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_predict_long_text(self, api_client):
        """Test prediction with long text"""
        response = await api_client.post(
            "/api/v1/predict",
            json={"text": TestData.LONG_TEXT}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] in ["positive", "negative"]


# Batch Prediction Tests
class TestBatchPrediction:
    @pytest.mark.asyncio
    async def test_batch_predict(self, api_client):
        """Test batch prediction"""
        response = await api_client.post(
            "/api/v1/predict/batch",
            json={"texts": TestData.BATCH_TEXTs}
        )
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert len(data["predictions"]) == len(TestData.BATCH_TEXTs)
        assert "total" in data
        assert data["total"] == len(TestData.BATCH_TEXTs)

    @pytest.mark.asyncio
    async def test_batch_predict_empty(self, api_client):
        """Test batch prediction with empty array"""
        response = await api_client.post(
            "/api/v1/predict/batch",
            json={"texts": []}
        )
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_batch_predict_single(self, api_client):
        """Test batch prediction with single text"""
        response = await api_client.post(
            "/api/v1/predict/batch",
            json={"texts": [TestData.POSITIVE_TEXT]}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["predictions"]) == 1


# Model Training Tests
class TestModelTraining:
    @pytest.mark.asyncio
    async def test_train_model(self, api_client):
        """Test model training"""
        response = await api_client.post(
            "/api/v1/train",
            json={"model_type": "logistic"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_type"] == "logistic"
        assert "accuracy" in data
        assert "training_samples" in data
        assert "validation_samples" in data
        assert "confusion_matrix" in data
        assert data["model_saved"] is True

    @pytest.mark.asyncio
    async def test_train_naive_bayes(self, api_client):
        """Test Naive Bayes training"""
        response = await api_client.post(
            "/api/v1/train",
            json={"model_type": "naive_bayes"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_type"] == "naive_bayes"

    @pytest.mark.asyncio
    async def test_train_with_parameters(self, api_client):
        """Test training with custom parameters"""
        response = await api_client.post(
            "/api/v1/train",
            json={
                "model_type": "logistic",
                "validation_split": 0.3,
                "random_seed": 123
            }
        )
        assert response.status_code == 200


# Model Evaluation Tests
class TestModelEvaluation:
    @pytest.mark.asyncio
    async def test_evaluate_model(self, api_client):
        """Test model evaluation"""
        response = await api_client.post("/api/v1/evaluate")
        assert response.status_code == 200
        data = response.json()
        assert "accuracy" in data
        assert "f1_score" in data
        assert "precision" in data
        assert "recall" in data
        assert "confusion_matrix" in data
        assert "total_samples" in data


# Model Info Tests
class TestModelInfo:
    @pytest.mark.asyncio
    async def test_get_model_info(self, api_client):
        """Test getting model information"""
        response = await api_client.get("/api/v1/model")
        assert response.status_code == 200
        data = response.json()
        assert "model_type" in data
        assert "trained" in data


# Dataset Info Tests
class TestDatasetInfo:
    @pytest.mark.asyncio
    async def test_get_dataset_info(self, api_client):
        """Test getting dataset information"""
        response = await api_client.get("/api/v1/dataset")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "total_samples" in data
        assert "positive_samples" in data
        assert "negative_samples" in data


# Training History Tests
class TestTrainingHistory:
    @pytest.mark.asyncio
    async def test_get_training_history(self, api_client):
        """Test getting training history"""
        response = await api_client.get("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# Keyword Analysis Tests
class TestKeywordAnalysis:
    @pytest.mark.asyncio
    async def test_analyze_keywords(self, api_client):
        """Test keyword analysis"""
        response = await api_client.post(
            "/api/v1/keywords/analyze",
            json={"text": TestData.POSITIVE_TEXT}
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_sentiment" in data
        assert "keywords" in data
        assert "positive_keywords" in data
        assert "negative_keywords" in data

    @pytest.mark.asyncio
    async def test_keyword_trends(self, api_client):
        """Test keyword trends"""
        response = await api_client.get("/api/v1/keywords/trends")
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
        assert isinstance(data["trends"], list)

    @pytest.mark.asyncio
    async def test_top_keywords_positive(self, api_client):
        """Test top positive keywords"""
        response = await api_client.get("/api/v1/keywords/top/positive?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "positive"
        assert "keywords" in data

    @pytest.mark.asyncio
    async def test_top_keywords_negative(self, api_client):
        """Test top negative keywords"""
        response = await api_client.get("/api/v1/keywords/top/negative?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "negative"

    @pytest.mark.asyncio
    async def test_keyword_frequency(self, api_client):
        """Test keyword frequency"""
        response = await api_client.get("/api/v1/keywords/frequency?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data


# Error Handling Tests
class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, api_client):
        """Test invalid endpoint"""
        response = await api_client.get("/api/v1/invalid")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_method(self, api_client):
        """Test invalid HTTP method"""
        response = await api_client.put("/api/v1/predict")
        assert response.status_code in [405, 404]

    @pytest.mark.asyncio
    async def test_invalid_json(self, api_client):
        """Test invalid JSON input"""
        response = await api_client.post(
            "/api/v1/predict",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


# Performance Tests
class TestPerformance:
    @pytest.mark.asyncio
    async def test_prediction_response_time(self, api_client):
        """Test prediction response time"""
        start = datetime.now()
        response = await api_client.post(
            "/api/v1/predict",
            json={"text": TestData.POSITIVE_TEXT}
        )
        duration = (datetime.now() - start).total_seconds()
        assert response.status_code == 200
        assert duration < 5.0  # Should be under 5 seconds

    @pytest.mark.asyncio
    async def test_batch_response_time(self, api_client):
        """Test batch prediction response time"""
        texts = TestData.BATCH_TEXTs * 20  # 100 texts
        start = datetime.now()
        response = await api_client.post(
            "/api/v1/predict/batch",
            json={"texts": texts}
        )
        duration = (datetime.now() - start).total_seconds()
        assert response.status_code == 200
        assert duration < 30.0  # Should be under 30 seconds for 100 texts


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
