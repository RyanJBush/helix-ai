from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.sentiment import SentimentRecord
from app.schemas.briefing import TickerBriefingResponse, WatchlistRecapRequest, WatchlistRecapResponse
from app.services.aggregation_service import aggregation_service


class BriefingService:
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def ticker_briefing(self, db: Session, ticker: str, lookback_hours: int = 24) -> TickerBriefingResponse:
        ticker_upper = ticker.upper()
        aggregate = aggregation_service.summarize_ticker(db, ticker=ticker_upper, lookback_hours=lookback_hours)
        start = self._utc_now() - timedelta(hours=lookback_hours)
        rows = list(
            db.scalars(
                select(SentimentRecord).where(
                    and_(SentimentRecord.ticker == ticker_upper, SentimentRecord.created_at >= start)
                )
            )
        )

        topics: list[str] = []
        events: list[str] = []
        text = " ".join(row.text.lower() for row in rows)
        if any(word in text for word in ["guidance", "earnings", "eps", "revenue"]):
            topics.append("earnings")
            events.append("earnings_update")
        if any(word in text for word in ["launch", "product", "platform"]):
            topics.append("product")
            events.append("product_update")
        if any(word in text for word in ["rates", "inflation", "fed", "macro"]):
            topics.append("macro")
            events.append("macro_event")
        if not topics:
            topics.append("general")
            events.append("general_news")

        direction = "bullish" if aggregate.weighted_sentiment_score >= 0.1 else "bearish" if aggregate.weighted_sentiment_score <= -0.1 else "neutral"
        summary = (
            f"{ticker_upper} sentiment is {direction} over the past {lookback_hours}h. "
            f"Weighted sentiment={aggregate.weighted_sentiment_score:.3f}, confidence={aggregate.weighted_confidence:.3f}, "
            f"coverage={aggregate.article_count} articles."
        )
        confidence_note = (
            "Confidence is moderate/high." if aggregate.weighted_confidence >= 0.55 else "Confidence is low; treat as directional context only."
        )

        return TickerBriefingResponse(
            ticker=ticker_upper,
            summary=summary,
            key_topics=sorted(set(topics)),
            key_events=sorted(set(events)),
            confidence_note=confidence_note,
            generated_at=self._utc_now(),
        )

    def watchlist_recap(self, db: Session, payload: WatchlistRecapRequest) -> WatchlistRecapResponse:
        lines: list[str] = []
        tickers = [ticker.upper() for ticker in payload.tickers]
        for ticker in tickers:
            aggregate = aggregation_service.summarize_ticker(db, ticker=ticker, lookback_hours=payload.lookback_hours)
            direction = "↑" if aggregate.weighted_sentiment_score > 0.1 else "↓" if aggregate.weighted_sentiment_score < -0.1 else "→"
            lines.append(
                f"{ticker} {direction} score={aggregate.weighted_sentiment_score:.2f} conf={aggregate.weighted_confidence:.2f} n={aggregate.article_count}"
            )

        recap = " | ".join(lines) if lines else "No watchlist coverage for requested window."
        return WatchlistRecapResponse(generated_at=self._utc_now(), recap=recap, tickers=tickers)


briefing_service = BriefingService()
