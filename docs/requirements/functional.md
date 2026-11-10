# Functional Requirements

## Overview
This document describes the functional requirements for the Sentiment Analysis Application, which provides sentiment analysis capabilities for user comments and text data.

## 1. Core Functionality

### 1.1 Sentiment Prediction

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-001 | System shall classify text as positive or negative sentiment | High | Implemented |
| F-002 | System shall provide confidence score for predictions | High | Implemented |
| F-003 | System shall support batch prediction for multiple texts | High | Implemented |
| F-004 | System shall handle text input of up to 10,000 characters | Medium | Implemented |
| F-005 | System shall return prediction within 5 seconds for single text | Medium | Implemented |

### 1.2 Keyword Analysis

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-010 | System shall extract keywords from text | High | Implemented |
| F-011 | System shall score keywords by sentiment | High | Implemented |
| F-012 | System shall identify positive and negative keywords | High | Implemented |
| F-013 | System shall calculate overall sentiment from keywords | Medium | Implemented |
| F-014 | System shall support n-gram keyword extraction (1-3 words) | Medium | Implemented |

### 1.3 Model Management

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-020 | System shall train sentiment classification models | High | Implemented |
| F-021 | System shall support multiple model types (Logistic Regression, Naive Bayes, etc.) | High | Implemented |
| F-022 | System shall save trained models to disk | High | Implemented |
| F-023 | System shall load saved models | High | Implemented |
| F-024 | System shall evaluate model performance | Medium | Implemented |
| F-025 | System shall provide training metrics (accuracy, F1, precision, recall) | Medium | Implemented |

### 1.4 Dataset Management

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-030 | System shall load datasets from files | High | Implemented |
| F-031 | System shall support CSV format | High | Implemented |
| F-032 | System shall support JSON format | High | Implemented |
| F-033 | System shall support TSV format | Medium | Implemented |
| F-034 | System shall auto-detect dataset format | Medium | Implemented |
| F-035 | System shall handle custom column mappings | Medium | Implemented |
| F-036 | System shall provide dataset statistics | Medium | Implemented |

## 2. API Functionality

### 2.1 REST API

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-100 | System shall provide RESTful API endpoints | High | Implemented |
| F-101 | API shall support JSON request/response | High | Implemented |
| F-102 | API shall have health check endpoint | Medium | Implemented |
| F-103 | API shall have sentiment prediction endpoint | High | Implemented |
| F-104 | API shall have batch prediction endpoint | High | Implemented |
| F-105 | API shall have model training endpoint | High | Implemented |
| F-106 | API shall have model evaluation endpoint | Medium | Implemented |
| F-107 | API shall have dataset info endpoint | Medium | Implemented |
| F-108 | API shall have keyword analysis endpoint | High | Implemented |

### 2.2 API Documentation

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-110 | API shall have OpenAPI/Swagger documentation | Medium | Implemented |
| F-111 | API shall have interactive documentation | Medium | Implemented |
| F-112 | API shall have endpoint descriptions | Medium | Implemented |

## 3. User Interface

### 3.1 Web Interface

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-200 | System shall have responsive web interface | High | Implemented |
| F-201 | UI shall support desktop browsers | High | Implemented |
| F-202 | UI shall support mobile browsers | Medium | Implemented |
| F-203 | UI shall have navigation between pages | High | Implemented |

### 3.2 Pages

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-210 | UI shall have Home page with overview | High | Implemented |
| F-211 | UI shall have Single Prediction page | High | Implemented |
| F-212 | UI shall have Batch Prediction page | High | Implemented |
| F-213 | UI shall have Keyword Analysis page | High | Implemented |
| F-214 | UI shall have Model Training page | High | Implemented |
| F-215 | UI shall have Model Evaluation page | Medium | Implemented |
| F-216 | UI shall have Dataset page | Medium | Implemented |

### 3.3 UI Features

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-220 | UI shall display prediction results with sentiment | High | Implemented |
| F-221 | UI shall display confidence scores | High | Implemented |
| F-222 | UI shall display keyword breakdown | Medium | Implemented |
| F-223 | UI shall display charts and visualizations | Medium | Implemented |
| F-224 | UI shall have form validation | Medium | Implemented |
| F-225 | UI shall have loading indicators | Medium | Implemented |
| F-226 | UI shall have error messages | Medium | Implemented |
| F-227 | UI shall have history of previous predictions | Medium | Implemented |

## 4. Data Processing

### 4.1 Text Processing

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-300 | System shall clean text (remove special characters) | High | Implemented |
| F-301 | System shall tokenize text | High | Implemented |
| F-302 | System shall remove stop words | High | Implemented |
| F-303 | System shall lemmatize text | Medium | Implemented |
| F-304 | System shall handle case normalization | High | Implemented |

### 4.2 Feature Extraction

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-310 | System shall extract TF-IDF features | High | Implemented |
| F-311 | System shall extract n-gram features | Medium | Implemented |
| F-312 | System shall extract HashingTF features | High | Implemented |

## 5. Model Types

### 5.1 Classification Models

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-400 | System shall support Logistic Regression | High | Implemented |
| F-401 | System shall support Naive Bayes | High | Implemented |
| F-402 | System shall support Random Forest | Medium | Implemented |
| F-403 | System shall support Gradient Boosted Trees | Medium | Implemented |

## 6. Error Handling

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-500 | System shall handle invalid input gracefully | High | Implemented |
| F-501 | System shall return meaningful error messages | High | Implemented |
| F-502 | System shall log errors | Medium | Implemented |
| F-503 | System shall handle dataset loading errors | Medium | Implemented |
| F-504 | System shall handle model training errors | Medium | Implemented |

## 7. Performance

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-600 | System shall handle datasets with 1000+ samples | Medium | Implemented |
| F-601 | System shall process batch of 100 texts in < 30 seconds | Medium | Implemented |
| F-602 | System shall use efficient data structures | Medium | Implemented |

## 8. Security

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F-700 | API shall validate all inputs | High | Implemented |
| F-701 | API shall sanitize outputs | High | Implemented |
| F-702 | API shall have CORS protection | Medium | Implemented |
| F-703 | API shall have request logging | Medium | Implemented |

## Requirements Summary

### By Priority
- **High Priority**: 30 requirements
- **Medium Priority**: 25 requirements
- **Low Priority**: 0 requirements

### By Status
- **Implemented**: 55 requirements
- **Not Implemented**: 0 requirements

### By Category
- Core Functionality: 19 requirements
- API Functionality: 11 requirements
- User Interface: 19 requirements
- Data Processing: 9 requirements
- Error Handling: 5 requirements
- Performance: 3 requirements
- Security: 4 requirements

## Traceability Matrix

| Feature | Requirements | Implementation |
|---------|--------------|----------------|
| Single Prediction | F-001, F-002, F-004, F-005 | backend/routes/sentiment.py |
| Batch Prediction | F-003, F-104 | backend/routes/sentiment.py |
| Keyword Analysis | F-010, F-011, F-012, F-013, F-014 | backend/routes/keywords.py |
| Model Training | F-020, F-021, F-022, F-023, F-024, F-025 | backend/routes/sentiment.py |
| Dataset Loading | F-030, F-031, F-032, F-033, F-034, F-035, F-036 | backend/core/dataset_parser.py |
| Text Processing | F-300, F-301, F-302, F-303 | backend/core/sentiment_trainer.py |
| Feature Extraction | F-310, F-311, F-312 | backend/core/sentiment_trainer.py |
| UI Pages | F-210-F-227 | frontend/src/pages/ |
| API Endpoints | F-100-F-112 | backend/main.py, backend/routes/ |

## Changes History

| Date | Version | Changes |
|------|---------|---------|
| 2024-XX-XX | 1.0 | Initial requirements document |
