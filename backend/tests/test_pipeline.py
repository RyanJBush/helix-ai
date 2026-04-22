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
    assert "duplicates_skipped" in status.json()
    assert "source_stats" in status.json()

    sentiment = client.post(
        "/api/v1/sentiment/analyze",
        json={
            "ticker": "AAPL",
            "source": "earnings_wire",
            "headline": "Apple beats estimates and raises guidance",
            "body": "Apple reported margin expansion and strong demand trends across products.",
            "compare_models": True,
        },
    )
    assert sentiment.status_code == 200
    body = sentiment.json()
    assert body["ticker"] == "AAPL"
    assert body["label"] in {"positive", "negative", "neutral"}
    assert 0 <= body["score"] <= 1
    assert 0 <= body["confidence"] <= 1
    assert "headline_score" in body
    assert "body_score" in body
    assert isinstance(body["topics"], list)
    assert isinstance(body["entity_sentiment"], dict)
    assert body["model_comparison"] is not None
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
    assert "factors" in signal.json()


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

    metrics = client.get("/api/v1/analytics/ticker/MSFT/metrics?lookback_hours=120&bucket_hours=6")
    assert metrics.status_code == 200
    metrics_body = metrics.json()
    assert metrics_body["ticker"] == "MSFT"
    assert isinstance(metrics_body["points"], list)

    overview = client.get("/api/v1/analytics/overview?lookback_hours=120&watchlist=MSFT&watchlist=AAPL")
    assert overview.status_code == 200
    overview_body = overview.json()
    assert "articles_processed" in overview_body
    assert "watchlist_alerts" in overview_body

    events = client.get("/api/v1/analytics/events/distribution?lookback_hours=120")
    assert events.status_code == 200
    assert isinstance(events.json(), list)

    clusters = client.get("/api/v1/analytics/topics/clusters?lookback_hours=120")
    assert clusters.status_code == 200
    assert isinstance(clusters.json(), list)

    article_table = client.get("/api/v1/analytics/ticker/MSFT/articles?lookback_hours=120&limit=10&offset=0")
    assert article_table.status_code == 200
    assert article_table.json()["ticker"] == "MSFT"

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
    assert "cumulative_benchmark_return" in backtest_body
    assert "confusion_matrix" in backtest_body
    assert "return_correlation" in backtest_body
    assert "next_day_return" in backtest_body["results"][0]

    tuning = client.post(
        "/api/v1/backtesting/tune",
        json={
            "ticker": "MSFT",
            "start_date": str(date.today() - timedelta(days=5)),
            "end_date": str(date.today()),
            "buy_thresholds": [0.1, 0.2],
            "sell_thresholds": [-0.1, -0.2],
            "min_confidences": [0.1, 0.3],
        },
    )
    assert tuning.status_code == 200
    tuning_body = tuning.json()
    assert tuning_body["tested_candidates"] >= 1
    assert "best_candidate" in tuning_body

    paper = client.post(
        "/api/v1/backtesting/paper-trade",
        json={
            "ticker": "MSFT",
            "start_date": str(date.today() - timedelta(days=5)),
            "end_date": str(date.today()),
            "initial_cash": 20000,
            "position_size": 0.25,
            "buy_threshold": 0.1,
            "sell_threshold": -0.1,
            "min_confidence": 0.1,
        },
    )
    assert paper.status_code == 200
    paper_body = paper.json()
    assert paper_body["ticker"] == "MSFT"
    assert "final_portfolio_value" in paper_body


def test_watchlist_signal_generation(client) -> None:
    client.post(
        "/api/v1/sentiment/analyze",
        json={"ticker": "NVDA", "source": "financial_news", "text": "Nvidia beat earnings expectations and raised guidance."},
    )
    watchlist = client.post(
        "/api/v1/signals/watchlist",
        json={
            "tickers": ["NVDA", "AAPL"],
            "buy_threshold": 0.1,
            "sell_threshold": -0.1,
            "min_confidence": 0.1,
            "lookback_hours": 72,
        },
    )
    assert watchlist.status_code == 200
    body = watchlist.json()
    assert isinstance(body["signals"], list)
    assert len(body["signals"]) == 2
    assert all("signal_strength" in signal for signal in body["signals"])

    alerts = client.get("/api/v1/signals/watchlist/alerts?tickers=NVDA&tickers=AAPL&lookback_hours=72")
    assert alerts.status_code == 200
    assert "alerts" in alerts.json()


def test_trust_explanations_annotations_and_briefings(client) -> None:
    client.post(
        "/api/v1/sentiment/analyze",
        json={"ticker": "AMZN", "source": "financial_news", "text": "Amazon beats revenue estimates and raises guidance."},
    )
    client.get("/api/v1/signals/ticker/AMZN?buy_threshold=0.1&sell_threshold=-0.1&min_confidence=0.1")

    explanation = client.get("/api/v1/trust/signals/AMZN/explanation?lookback_hours=48&top_n=3")
    assert explanation.status_code == 200
    explanation_body = explanation.json()
    assert explanation_body["ticker"] == "AMZN"
    assert "top_contributors" in explanation_body

    annotation = client.post(
        "/api/v1/trust/annotations",
        json={"ticker": "AMZN", "author": "qa_analyst", "note": "Signal aligns with guidance strength."},
    )
    assert annotation.status_code == 200
    assert annotation.json()["ticker"] == "AMZN"

    listed = client.get("/api/v1/trust/annotations/AMZN")
    assert listed.status_code == 200
    assert len(listed.json()) >= 1
    paged = client.get("/api/v1/trust/annotations/AMZN?limit=1&offset=0")
    assert paged.status_code == 200
    assert len(paged.json()) == 1

    audit = client.get("/api/v1/trust/signals/AMZN/audit")
    assert audit.status_code == 200
    assert "entries" in audit.json()

    briefing = client.get("/api/v1/briefings/ticker/AMZN?lookback_hours=48")
    assert briefing.status_code == 200
    assert "summary" in briefing.json()

    recap = client.post("/api/v1/briefings/watchlist", json={"tickers": ["AMZN", "AAPL"], "lookback_hours": 24})
    assert recap.status_code == 200
    assert "recap" in recap.json()


def test_sentiment_fallback_scoring() -> None:
    label, score = nlp_service._fallback_score("Company beats earnings and records strong growth")
    assert label == "positive"
    assert score > 0.5


def test_platform_readiness_tracing_and_replay(client) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.headers.get("X-Request-Id")

    readiness = client.get("/readiness")
    assert readiness.status_code == 200
    assert readiness.json()["status"] == "ready"

    replay = client.post("/api/v1/replay", json={"tickers": ["AAPL", "MSFT"], "steps": 3, "seed": 7})
    assert replay.status_code == 200
    replay_body = replay.json()
    assert len(replay_body["events"]) == 6
    assert replay_body["events"][0]["ticker"] in {"AAPL", "MSFT"}

    ingestion_job = client.post(
        "/api/v1/jobs/ingestion",
        json={
            "payload": {
                "tickers": ["AAPL"],
                "limit_per_ticker": 1,
                "sources": ["financial_news"],
                "mode": "realtime",
                "lookback_days": 3,
            }
        },
    )
    assert ingestion_job.status_code == 200
    ingestion_job_body = ingestion_job.json()
    fetched = client.get(f"/api/v1/jobs/{ingestion_job_body['job_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] in {"completed", "running", "queued"}

    sentiment_job = client.post(
        "/api/v1/jobs/sentiment-batch",
        json={
            "items": [
                {
                    "ticker": "AAPL",
                    "text": "Apple beats guidance and margin expectations.",
                    "source": "financial_news",
                },
                {
                    "ticker": "MSFT",
                    "headline": "Microsoft cloud guidance rises",
                    "body": "Microsoft reported strong enterprise demand.",
                    "source": "financial_news",
                },
            ]
        },
    )
    assert sentiment_job.status_code == 200
    assert sentiment_job.json()["job_type"] == "sentiment_batch"
