# System Architecture Documentation

## Overview
The Sentiment Analysis Application uses a modular architecture with PySpark for ML, FastAPI for backend, and React+Vite for frontend.

## High-Level Architecture

```
Frontend (React+Vite) -> FastAPI Backend -> PySpark ML -> Datasets
```

## Components

### Frontend
- React 18 with TypeScript
- Vite build system
- React Query for data fetching
- Zustand for state management
- Tailwind CSS for styling
- Recharts for visualization

### Backend
- FastAPI REST API
- PySpark ML for sentiment analysis
- Pydantic for validation
- Multiple dataset parsers

### Data Processing
- PySpark distributed computing
- NLTK for text processing
- Custom keyword analysis

## Deployment
- Development: Local PySpark + FastAPI + Vite
- Production: Docker containers with load balancing
