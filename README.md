# Helix AI

Real-time stock sentiment and trading intelligence platform using NLP, streaming data, and a full-stack analytics dashboard.

## Monorepo Structure

- `backend/` – FastAPI API, sentiment logic, WebSocket stream, pytest/ruff
- `frontend/` – React + Vite + Tailwind app with Recharts visualizations
- `docs/` – architecture and project docs
- Root tooling: `Makefile`, `docker-compose.yml`, `.editorconfig`, GitHub Actions CI

## Backend MVP Endpoints

- `GET /health`
- `POST /api/data/ingest`
- `GET /api/data/news`
- `POST /api/sentiment/analyze`
- `GET /api/sentiment/{ticker}`
- `GET /api/signals/{ticker}`
- `GET /api/dashboard/summary`
- `WebSocket /ws/stream`

Backend data model targets production PostgreSQL entities:
- `news_articles`
- `sentiment_scores`
- `aggregated_sentiment`
- `trading_signals`

## Frontend MVP Pages

- Login
- Dashboard
- Ticker View
- News Feed
- Signals

Includes KPI cards, sentiment charts, ticker filters, and real-time updates from WebSocket stream events.

## Local Development

### Option 1: Docker Compose

```bash
docker-compose up --build
```

### Option 2: Manual

Backend:

```bash
cd backend
python -m pip install '.[dev]'
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Validation

Backend:

```bash
make lint-backend
make test-backend
```

Frontend:

```bash
make lint-frontend
make build-frontend
```
