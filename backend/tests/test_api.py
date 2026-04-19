from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ingest_analyze_and_summary() -> None:
    ingest_response = client.post(
        "/api/data/ingest",
        json={
            "articles": [
                {
                    "ticker": "AAPL",
                    "source": "unit-test",
                    "title": "Apple posts strong growth",
                    "content": "Apple posts strong growth and upgrades outlook",
                }
            ]
        },
    )
    assert ingest_response.status_code == 200
    assert ingest_response.json()["ingested"] >= 1

    analyze_response = client.post("/api/sentiment/analyze", json={"ticker": "AAPL"})
    assert analyze_response.status_code == 200
    assert analyze_response.json()["analyzed"] >= 1

    sentiment_response = client.get("/api/sentiment/AAPL")
    assert sentiment_response.status_code == 200

    signal_response = client.get("/api/signals/AAPL")
    assert signal_response.status_code == 200

    summary_response = client.get("/api/dashboard/summary")
    assert summary_response.status_code == 200
    assert summary_response.json()["tracked_tickers"] >= 1


def test_websocket_stream_summary_event() -> None:
    with client.websocket_connect("/ws/stream") as websocket:
        message = websocket.receive_json()
    assert message["event"] == "summary"
    assert "payload" in message
