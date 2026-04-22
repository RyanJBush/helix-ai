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
   - Supports headline/body decomposition, topic/event extraction, entity attribution, and optional baseline-vs-advanced model comparison.
4. `GET /api/v1/analytics/ticker/{ticker}` (weighted aggregation)
5. `GET /api/v1/analytics/ticker/{ticker}/drilldown` (ticker drill-down metrics/history)
6. `GET /api/v1/analytics/ticker/{ticker}/metrics` (bucketed sentiment metrics time series)
7. `GET /api/v1/analytics/overview`, `GET /api/v1/analytics/events/distribution`, `GET /api/v1/analytics/topics/clusters` (dashboard KPI + event/topic analytics)
8. `GET /api/v1/analytics/ticker/{ticker}/articles` (paginated per-article sentiment table for ticker drill-down)
9. `GET /api/v1/signals/ticker/{ticker}` (weighted thresholds with tunable params)
   - Supports multifactor context inputs (event impact, volume z-score, momentum), cooldown conflict handling, and sharp-shift alerts.
10. `POST /api/v1/signals/watchlist` (watchlist-wide weighted signals)
11. `GET /api/v1/signals/watchlist/alerts` (watchlist alert center for sharp-shift/low-confidence monitoring)
12. `POST /api/v1/backtesting` (historical backtest scaffolding + benchmark/precision metrics)
   - Includes next-day return proxy, intraday move proxy, volatility-change proxy, and return correlation.
13. `POST /api/v1/backtesting/tune` (threshold tuning grid search)
14. `POST /api/v1/backtesting/paper-trade` (paper-trading simulation ledger)
15. `WS /api/v1/streaming/ws` (real-time updates)
16. `GET /api/v1/trust/signals/{ticker}/explanation` (article-to-signal traceability + contradiction detection)
17. `POST /api/v1/trust/annotations` and `GET /api/v1/trust/annotations/{ticker}` (analyst annotation workflow)
18. `GET /api/v1/trust/signals/{ticker}/audit` (signal audit trail)
19. `GET /api/v1/briefings/ticker/{ticker}` and `POST /api/v1/briefings/watchlist` (AI-style ticker briefings and watchlist recaps)
20. `POST /api/v1/replay` (seeded replay mode for deterministic demo/event playback)
21. `POST /api/v1/jobs/ingestion`, `POST /api/v1/jobs/sentiment-batch`, `GET /api/v1/jobs/{job_id}` (background jobs + status tracking)

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

### Operational checks
- `GET /health` for liveness
- `GET /readiness` for DB-backed readiness probe
- All API responses include `X-Request-Id` for traceability

## Example tickers
- `AAPL`
- `MSFT`
- `TSLA`
- `NVDA`

## Next Steps
- Connect ingestion to a real market/news provider.
- Add auth, migrations, and scheduling.
- Implement charting library + richer portfolio analytics.
