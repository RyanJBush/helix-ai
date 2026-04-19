from datetime import datetime

from sqlalchemy.orm import Session

from app.models.news import NewsItem
from app.schemas.news import NewsItemResponse


MOCK_HEADLINES = {
    "AAPL": [
        "Apple beats iPhone unit expectations in Q2",
        "Services revenue hits new quarterly record",
        "Analysts debate margin outlook after guidance",
    ],
    "TSLA": [
        "Tesla cuts prices in key global markets",
        "EV demand trends show signs of stabilization",
        "Autonomy roadmap receives mixed analyst reaction",
    ],
    "MSFT": [
        "Microsoft cloud growth remains resilient",
        "AI copilots drive enterprise upsell momentum",
        "Regulators review cloud licensing practices",
    ],
}


class NewsIngestionService:
    def ingest_mock_news(self, db: Session, tickers: list[str], limit_per_ticker: int) -> list[NewsItemResponse]:
        inserted: list[NewsItemResponse] = []

        for raw_ticker in tickers:
            ticker = raw_ticker.upper()
            headlines = MOCK_HEADLINES.get(ticker, [f"{ticker} trades flat as investors await catalyst"])

            for idx, headline in enumerate(headlines[:limit_per_ticker]):
                item = NewsItem(
                    ticker=ticker,
                    source="mock-wire",
                    headline=headline,
                    content=f"{headline}. Placeholder article paragraph {idx + 1}.",
                    published_at=datetime.utcnow(),
                )
                db.add(item)
                inserted.append(
                    NewsItemResponse(
                        ticker=ticker,
                        source=item.source,
                        headline=item.headline,
                        content=item.content,
                        published_at=item.published_at,
                    )
                )

        db.commit()
        return inserted


news_ingestion_service = NewsIngestionService()
