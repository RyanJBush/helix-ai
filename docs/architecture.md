# Helix AI Architecture (MVP)

- **Backend**: FastAPI service exposing ingestion, sentiment, signals, dashboard, and WebSocket stream endpoints.
- **NLP**: HuggingFace Transformers pipeline with FinBERT fallback logic.
- **Data layer**: MVP in-memory store with schema mapped to production PostgreSQL entities (`news_articles`, `sentiment_scores`, `aggregated_sentiment`, `trading_signals`).
- **Frontend**: React + Vite + Tailwind dashboard with live sentiment and trading insights.
- **Infra**: Docker Compose for local orchestration and GitHub Actions CI for lint/tests/build.
