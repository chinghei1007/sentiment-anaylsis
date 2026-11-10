# Sentiment Analysis Application - Documentation

This directory contains comprehensive documentation for the Sentiment Analysis application built with PySpark, FastAPI, React, and Vite.

## Documentation Structure

```
docs/
├── README.md                    # This file
├── architecture/
│   ├── system-architecture.md    # System architecture overview
│   ├── backend-architecture.md   # Backend architecture details
│   ├── frontend-architecture.md  # Frontend architecture details
│   └── data-flow.md             # Data flow diagrams
├── requirements/
│   ├── functional.md            # Functional requirements
│   ├── non-functional.md         # Non-functional requirements
│   └── user-stories.md           # User stories
├── testing/
│   ├── TESTED.md                # Test coverage and results
│   ├── e2e-test-plan.md          # E2E test plan
│   ├── unit-tests.md             # Unit test documentation
│   └── integration-tests.md       # Integration test documentation
└── api/
    ├── endpoints.md              # API endpoint documentation
    └── schemas.md                # API schema definitions
```

## Quick Links

- [System Architecture](./architecture/system-architecture.md)
- [Functional Requirements](./requirements/functional.md)
- [API Documentation](./api/endpoints.md)
- [Test Coverage Report](./testing/TESTED.md)

## Application Overview

The Sentiment Analysis Application provides:

1. **Document-Level Sentiment Analysis**: Classify entire texts as positive or negative
2. **Keyword-Level Sentiment Analysis**: Identify sentiment-driving keywords within text
3. **Batch Processing**: Analyze multiple texts simultaneously
4. **Model Training**: Train custom ML models on your datasets
5. **Model Evaluation**: Evaluate model performance with detailed metrics
6. **Flexible Dataset Parsing**: Support for CSV, JSON, TSV, and common dataset formats

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, PySpark ML, Python 3.10+ |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Data Processing | PySpark, NLTK, scikit-learn |
| State Management | Zustand, React Query |
| UI Components | Recharts, Lucide Icons |
| Build Tools | Vite, esbuild |

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Documentation Conventions

- **Architecture Docs**: Describe system design and component interactions
- **Requirements Docs**: Define functional and non-functional requirements
- **Testing Docs**: Document test cases, coverage, and results
- **API Docs**: Describe endpoints, schemas, and usage examples

## Contributing to Documentation

1. Keep documentation up-to-date with code changes
2. Use consistent formatting and structure
3. Include diagrams where helpful
4. Document both success and error cases
5. Provide examples for complex concepts

## License

This documentation is part of the Sentiment Analysis Application and is licensed under the same terms as the application itself.
