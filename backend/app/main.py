from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import AnalyzeRequest, IngestRequest, NewsArticleIn
from app.services.sentiment import SentimentAnalyzer
from app.services.store import DataStore

app = FastAPI(title="Helix AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = DataStore()
analyzer = SentimentAnalyzer()


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event: str, payload: dict) -> None:
        dead: list[WebSocket] = []
        message = {"event": event, "payload": payload, "timestamp": datetime.now(UTC).isoformat()}
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.disconnect(connection)


manager = ConnectionManager()


def _simulated_news_items(count: int) -> list[NewsArticleIn]:
    templates = [
        ("AAPL", "Apple shares rally as services growth beats expectations"),
        ("TSLA", "Tesla faces margin risk as deliveries miss forecast"),
        ("MSFT", "Microsoft cloud momentum remains strong after upgrade"),
        ("NVDA", "NVIDIA valuation falls amid broader semiconductor weakness"),
        ("AMZN", "Amazon retail trends stabilize with stronger demand"),
    ]
    simulated: list[NewsArticleIn] = []
    for idx in range(count):
        ticker, headline = templates[idx % len(templates)]
        simulated.append(
            NewsArticleIn(
                ticker=ticker,
                source="simulated-feed",
                title=headline,
                content=headline,
            )
        )
    return simulated


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/data/ingest")
async def ingest_data(request: IngestRequest):
    articles = list(request.articles)
    if request.simulate_count:
        articles.extend(_simulated_news_items(request.simulate_count))

    ingested = store.ingest(articles)
    await manager.broadcast("news_ingested", {"count": len(ingested)})
    return {"ingested": len(ingested), "items": ingested}


@app.get("/api/data/news")
async def get_news(ticker: str | None = None, limit: int = 50):
    return {"items": store.list_news(ticker=ticker, limit=limit)}


@app.post("/api/sentiment/analyze")
async def analyze_sentiment(request: AnalyzeRequest):
    existing_ids = {record.article_id for record in store.sentiment_scores}
    candidates = [
        article
        for article in store.news_articles
        if article.id not in existing_ids
        and (request.ticker is None or article.ticker == request.ticker.upper())
    ]

    analyzed = []
    for article in candidates:
        score, label = analyzer.analyze(f"{article.title}. {article.content}")
        analyzed.append(store.add_sentiment(article, score, label))

    await manager.broadcast("sentiment_updated", {"count": len(analyzed)})
    return {"analyzed": len(analyzed), "items": analyzed}


@app.get("/api/sentiment/{ticker}")
async def get_sentiment(ticker: str):
    sentiment = store.get_sentiment(ticker)
    if not sentiment:
        return JSONResponse(status_code=404, content={"detail": "Ticker sentiment not found"})
    return sentiment


@app.get("/api/signals/{ticker}")
async def get_signal(ticker: str):
    signal = store.get_signal(ticker)
    if not signal:
        return JSONResponse(status_code=404, content={"detail": "Ticker signal not found"})
    return signal


@app.get("/api/dashboard/summary")
async def dashboard_summary():
    return store.dashboard_summary()


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json(
            {
                "event": "summary",
                "payload": store.dashboard_summary().model_dump(),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        while True:
            await asyncio.sleep(3)
            await websocket.send_json(
                {
                    "event": "summary",
                    "payload": store.dashboard_summary().model_dump(),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
