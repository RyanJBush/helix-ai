# Helix AI Architecture

## Services
- **FastAPI backend**: REST + WebSocket endpoints for ingestion, sentiment scoring, aggregation, and signal generation.
- **React frontend dashboard**: Fintech-style multi-page UI (Dashboard, Ticker View, News Feed, Signals).
- **PostgreSQL**: Durable store for news items, sentiment records, and generated signals.
- **Transformers NLP**: FinBERT inference pipeline with deterministic fallback heuristic.

## API Surface
- `POST /api/v1/news/ingest`
- `POST /api/v1/sentiment/analyze`
- `GET /api/v1/analytics/ticker/{ticker}`
- `GET /api/v1/signals/ticker/{ticker}`
- `GET /api/v1/streaming/status`
- `WS /api/v1/streaming/ws`

## UI Surface
- Dashboard: KPI cards, trend chart, event tape.
- Ticker View: ticker-filtered sentiment and signal detail.
- News Feed: ticker-filtered ingestion/news rows.
- Signals: signal table and real-time stream score panel.

## Pipeline Workflow
1. Ingest news articles (mock feed for selected tickers).
2. Analyze sentiment per headline/article.
3. Persist sentiment + aggregate per ticker over rolling windows.
4. Generate BUY/SELL/HOLD signal based on sentiment breadth and score thresholds.
5. Push real-time sentiment updates to WebSocket subscribers.
