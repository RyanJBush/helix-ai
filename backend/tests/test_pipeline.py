from datetime import date, timedelta

from app.services.nlp_service import nlp_service


def test_news_ingest_and_sentiment_pipeline(client) -> None:
    ingest = client.post(
        "/api/v1/news/ingest",
        json={
            "tickers": ["AAPL", "TSLA"],
            "limit_per_ticker": 2,
            "sources": ["financial_news", "social_curated"],
            "mode": "historical_backfill",
            "lookback_days": 7,
        },
    )
    assert ingest.status_code == 200
    assert len(ingest.json()) == 8
    assert ingest.headers.get("X-Ingestion-Run-Id")
    assert all("source_weight" in row for row in ingest.json())

    run_id = int(ingest.headers["X-Ingestion-Run-Id"])
    status = client.get(f"/api/v1/news/ingest/status/{run_id}")
    assert status.status_code == 200
    assert status.json()["records_inserted"] == len(ingest.json())

    sentiment = client.post(
        "/api/v1/sentiment/analyze",
        json={
            "ticker": "AAPL",
            "source": "earnings_wire",
            "text": "Apple beats estimates and raises guidance with strong margin expansion.",
        },
    )
    assert sentiment.status_code == 200
    body = sentiment.json()
    assert body["ticker"] == "AAPL"
    assert body["label"] in {"positive", "negative", "neutral"}
    assert 0 <= body["score"] <= 1
    assert 0 <= body["confidence"] <= 1
    assert "model_used" in body

    aggregate = client.get("/api/v1/analytics/ticker/AAPL")
    assert aggregate.status_code == 200
    aggregation_body = aggregate.json()
    assert aggregation_body["ticker"] == "AAPL"
    assert aggregation_body["article_count"] >= 1
    assert "weighted_sentiment_score" in aggregation_body
    assert "weighted_confidence" in aggregation_body

    signal = client.get("/api/v1/signals/ticker/AAPL?buy_threshold=0.1&sell_threshold=-0.1&min_confidence=0.1")
    assert signal.status_code == 200
    assert signal.json()["signal"] in {"BUY", "SELL", "HOLD"}
    assert "weighted_score" in signal.json()


def test_ticker_drilldown_and_backtest_scaffold(client) -> None:
    client.post(
        "/api/v1/sentiment/analyze",
        json={
            "ticker": "MSFT",
            "source": "financial_news",
            "text": "Microsoft posts strong cloud growth and improves full-year guidance.",
        },
    )
    client.post(
        "/api/v1/sentiment/analyze",
        json={
            "ticker": "MSFT",
            "source": "social_curated",
            "text": "Social sentiment stays mixed with volatile reactions to Microsoft's valuation.",
        },
    )

    drilldown = client.get("/api/v1/analytics/ticker/MSFT/drilldown?lookback_hours=120")
    assert drilldown.status_code == 200
    drilldown_body = drilldown.json()
    assert drilldown_body["ticker"] == "MSFT"
    assert "aggregate" in drilldown_body
    assert isinstance(drilldown_body["sentiment_history"], list)

    backtest = client.post(
        "/api/v1/backtesting",
        json={
            "ticker": "MSFT",
            "start_date": str(date.today() - timedelta(days=5)),
            "end_date": str(date.today()),
            "buy_threshold": 0.1,
            "sell_threshold": -0.1,
            "min_confidence": 0.1,
        },
    )
    assert backtest.status_code == 200
    backtest_body = backtest.json()
    assert backtest_body["ticker"] == "MSFT"
    assert "results" in backtest_body
    assert "cumulative_proxy_return" in backtest_body


def test_sentiment_fallback_scoring() -> None:
    label, score = nlp_service._fallback_score("Company beats earnings and records strong growth")
    assert label == "positive"
    assert score > 0.5
