# Market Sentiment & Trading Intelligence Dashboard

## Executive Summary
This project is a full-stack **educational analytics platform** that demonstrates how financial news sentiment can be transformed into structured market intelligence workflows. It combines a FastAPI backend, sentiment and signal services, simulation-style backtesting, and a React dashboard for exploring ticker-level insights. The repository is designed as a recruiter-ready portfolio artifact for fintech, data science, analytics, and software engineering conversations.

## Market Intelligence Problem This Project Solves
Market commentary is noisy, unstructured, and difficult to operationalize consistently. This project shows an end-to-end approach for:
- ingesting and normalizing market/news-style records,
- scoring sentiment with explainable metadata,
- aggregating ticker-level sentiment into interpretable signals,
- evaluating those signals in **paper-trade/backtesting simulations** for decision-support analysis.

Rather than claiming execution systems, it focuses on transparent analysis pipelines and productized analytics UX.

## Key Features
- **News ingestion and scoring workflow** with deterministic/demo-friendly inputs and stored ingestion runs.
- **Sentiment analysis service** with score, confidence, label, and model metadata.
- **Ticker aggregation and signal generation** (weighted sentiment + thresholds + rationale).
- **Trust/explainability APIs** for signal context and explanation outputs.
- **Backtesting and paper-trade simulation endpoints** for scenario-style evaluation (no brokerage execution).
- **Replay, streaming, jobs, and briefing routes** to support richer analyst workflows.
- **React dashboard UI** with pages for dashboard metrics, ticker view, news feed, and signals.

## Tech Stack
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy.
- **Analytics/NLP:** pandas and NumPy-based processing plus sentiment service logic.
- **Frontend:** React, TypeScript, Vite, React Router.
- **Data layer:** SQLite by default (PostgreSQL-compatible via configuration patterns).
- **Developer tooling:** pytest, ESLint, Docker/Docker Compose, Makefile-driven workflows.

## Data and Sentiment Analysis Workflow
1. **Ingestion:** News items are ingested and tracked by run metadata.
2. **Sentiment scoring:** Each item is analyzed for polarity/score/confidence and persisted.
3. **Aggregation:** Sentiment is rolled up by ticker with lookback windows and weighting.
4. **Signal generation:** Aggregates are converted into buy/hold/sell-style outputs with rationale and thresholds.
5. **Simulation analytics:** Backtesting and paper-trade endpoints evaluate signal behavior on historical-style data.
6. **Delivery:** Results are exposed via API routes and displayed in the frontend pages/components.

> Included sample data (`data/sample_news.json`, `data/sample_prices.csv`) supports local demos and deterministic testing.

## Dashboard or Analytics Overview
The frontend includes route-level experiences for:
- **Dashboard page:** KPI and sentiment visualization components (including charts/gauges/panels).
- **Ticker page:** ticker-focused intelligence views.
- **News page:** feed exploration.
- **Signals page:** signal outputs and status context.

The backend API also provides health/readiness checks plus domain routers for news, sentiment, analytics, signals, backtesting, trust, streaming, replay, briefings, and jobs.

## Setup and Installation
### Option A: Run with Docker Compose
```bash
docker compose up --build
```

### Option B: Run locally (backend + frontend)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (in a second terminal)
cd frontend
npm install
npm run dev
```

### Seed demo data
```bash
cd backend
NLP_PROVIDER=heuristic PYTHONPATH=. python scripts/seed_demo.py
```

### Useful developer commands
```bash
make test-backend
make lint
make build-frontend
```

## Example Use Cases
- Build a **fintech case-study demo** showing sentiment-to-signal transformation.
- Demonstrate **data product engineering** across ingestion, modeling, APIs, and UI.
- Explore **decision-support workflows** for analyst tooling without live trading execution.
- Showcase **full-stack collaboration readiness** with typed API contracts and modular services.

## Skills Demonstrated
- Financial NLP workflow design and sentiment scoring integration.
- API-first backend engineering (routing, schemas, service layers, persistence).
- Analytics pipeline construction (aggregation, weighting, signal logic, simulation).
- Frontend analytics UX development (React + TypeScript components and routing).
- Testing and developer experience practices for reproducible local demos.

## Resume-Ready Project Description
Built a full-stack **Market Sentiment & Trading Intelligence Dashboard** that ingests and scores financial/news text, aggregates ticker-level sentiment, generates explainable trading signals, and evaluates strategies through backtesting and paper-trade simulation endpoints. Implemented modular FastAPI services and a React/TypeScript analytics UI to communicate decision-support insights in a recruiter-friendly product format.

## Future Improvements
- Integrate clearly-labeled external data adapters with freshness/source provenance metadata.
- Expand model evaluation instrumentation (drift checks, calibration, benchmarking views).
- Add richer dashboard filtering/comparison workflows and deeper explainability visualizations.
- Strengthen productionization patterns (observability, background scheduling, deployment hardening).

## Disclaimer
This repository is for **educational and analytical purposes only**. It does **not** provide financial advice, does **not** execute real trades, and should not be used as an automated investment system.
