# Helix AI Monorepo

Simple but realistic scaffold for a real-time stock sentiment platform.

## Stack
- FastAPI backend (REST + WebSockets)
- React frontend (Vite + TypeScript)
- PostgreSQL persistence
- Hugging Face Transformers NLP (FinBERT + fallback)
- Docker compose for local orchestration
- GitHub Actions CI pipeline

## Frontend pages
- Dashboard
- Ticker View
- News Feed
- Signals

## Frontend features
- KPI cards and market summary
- Sentiment sparkline charts
- Ticker filtering and detail drilldowns
- Real-time event updates via WebSocket + mock stream fallback

## Implemented backend workflow
1. `POST /api/v1/news/ingest` (multi-source ingestion + dedupe + run tracking)
2. `GET /api/v1/news/ingest/status/{run_id}` (ingestion status)
3. `POST /api/v1/sentiment/analyze` (finance-aware sentiment + confidence)
4. `GET /api/v1/analytics/ticker/{ticker}` (weighted aggregation)
5. `GET /api/v1/analytics/ticker/{ticker}/drilldown` (ticker drill-down metrics/history)
6. `GET /api/v1/signals/ticker/{ticker}` (weighted thresholds with tunable params)
7. `POST /api/v1/backtesting` (historical backtest scaffolding)
8. `WS /api/v1/streaming/ws` (real-time updates)

## Quick Start
### Run with Docker
```bash
make up
```

### Run locally (split terminal)
```bash
# backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev
```

## Example tickers
- `AAPL`
- `MSFT`
- `TSLA`
- `NVDA`

## Next Steps
- Connect ingestion to a real market/news provider.
- Add auth, migrations, and scheduling.
- Implement charting library + richer portfolio analytics.
