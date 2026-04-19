from datetime import datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.sentiment import SentimentRecord
from app.schemas.analytics import TickerAggregationResponse


class AggregationService:
    def summarize_ticker(self, db: Session, ticker: str, lookback_hours: int = 24) -> TickerAggregationResponse:
        now = datetime.utcnow()
        start = now - timedelta(hours=lookback_hours)
        ticker_upper = ticker.upper()

        filters = and_(SentimentRecord.ticker == ticker_upper, SentimentRecord.created_at >= start)
        total = db.scalar(select(func.count()).select_from(SentimentRecord).where(filters)) or 0
        avg_score = db.scalar(select(func.avg(SentimentRecord.score)).where(filters)) or 0.0

        if total == 0:
            return TickerAggregationResponse(
                ticker=ticker_upper,
                article_count=0,
                avg_score=0.0,
                positive_ratio=0.0,
                neutral_ratio=0.0,
                negative_ratio=0.0,
                window_start=start,
                window_end=now,
            )

        def label_ratio(label: str) -> float:
            count = db.scalar(
                select(func.count()).select_from(SentimentRecord).where(filters, SentimentRecord.label.contains(label))
            ) or 0
            return round(count / total, 4)

        return TickerAggregationResponse(
            ticker=ticker_upper,
            article_count=total,
            avg_score=round(float(avg_score), 4),
            positive_ratio=label_ratio("pos") + label_ratio("positive"),
            neutral_ratio=label_ratio("neu") + label_ratio("neutral"),
            negative_ratio=label_ratio("neg") + label_ratio("negative"),
            window_start=start,
            window_end=now,
        )


aggregation_service = AggregationService()
