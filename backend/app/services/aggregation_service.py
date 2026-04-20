from datetime import datetime, timedelta

from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from app.models.sentiment import SentimentRecord
from app.models.signal import SignalRecord
from app.schemas.analytics import (
    SentimentMetricPoint,
    SignalMetricPoint,
    TickerAggregationResponse,
    TickerDrilldownResponse,
)
from app.services.weighting_service import market_hours_multiplier, time_decay_multiplier


class AggregationService:
    @staticmethod
    def _label_to_direction(label: str) -> float:
        lowered = label.lower()
        if "pos" in lowered:
            return 1.0
        if "neg" in lowered:
            return -1.0
        return 0.0

    def summarize_ticker(self, db: Session, ticker: str, lookback_hours: int = 24) -> TickerAggregationResponse:
        now = datetime.utcnow()
        start = now - timedelta(hours=lookback_hours)
        ticker_upper = ticker.upper()

        records = list(
            db.scalars(
                select(SentimentRecord).where(
                    and_(SentimentRecord.ticker == ticker_upper, SentimentRecord.created_at >= start)
                )
            )
        )

        if not records:
            return TickerAggregationResponse(
                ticker=ticker_upper,
                article_count=0,
                avg_score=0.0,
                avg_confidence=0.0,
                weighted_sentiment_score=0.0,
                weighted_confidence=0.0,
                positive_ratio=0.0,
                neutral_ratio=0.0,
                negative_ratio=0.0,
                source_breakdown={},
                window_start=start,
                window_end=now,
            )

        total = len(records)
        avg_score = sum(r.score for r in records) / total
        avg_confidence = sum(r.confidence for r in records) / total

        pos_count = 0
        neu_count = 0
        neg_count = 0
        source_breakdown: dict[str, int] = {}
        weighted_signal_numerator = 0.0
        weighted_confidence_numerator = 0.0
        total_weight = 0.0

        for record in records:
            direction = self._label_to_direction(record.label)
            if direction > 0:
                pos_count += 1
            elif direction < 0:
                neg_count += 1
            else:
                neu_count += 1

            source_breakdown[record.source] = source_breakdown.get(record.source, 0) + 1
            weight = record.source_weight * time_decay_multiplier(record.created_at, now=now)
            weight *= market_hours_multiplier(record.created_at)

            weighted_signal_numerator += direction * record.score * weight
            weighted_confidence_numerator += record.confidence * weight
            total_weight += weight

        weighted_sentiment_score = weighted_signal_numerator / total_weight if total_weight else 0.0
        weighted_confidence = weighted_confidence_numerator / total_weight if total_weight else 0.0

        return TickerAggregationResponse(
            ticker=ticker_upper,
            article_count=total,
            avg_score=round(avg_score, 4),
            avg_confidence=round(avg_confidence, 4),
            weighted_sentiment_score=round(weighted_sentiment_score, 4),
            weighted_confidence=round(weighted_confidence, 4),
            positive_ratio=round(pos_count / total, 4),
            neutral_ratio=round(neu_count / total, 4),
            negative_ratio=round(neg_count / total, 4),
            source_breakdown=source_breakdown,
            window_start=start,
            window_end=now,
        )

    def ticker_drilldown(self, db: Session, ticker: str, lookback_hours: int = 72) -> TickerDrilldownResponse:
        aggregate = self.summarize_ticker(db, ticker=ticker, lookback_hours=lookback_hours)
        start = aggregate.window_start
        ticker_upper = ticker.upper()

        sentiments = list(
            db.scalars(
                select(SentimentRecord)
                .where(and_(SentimentRecord.ticker == ticker_upper, SentimentRecord.created_at >= start))
                .order_by(desc(SentimentRecord.created_at))
                .limit(200)
            )
        )
        signals = list(
            db.scalars(
                select(SignalRecord)
                .where(and_(SignalRecord.ticker == ticker_upper, SignalRecord.created_at >= start))
                .order_by(desc(SignalRecord.created_at))
                .limit(200)
            )
        )

        return TickerDrilldownResponse(
            ticker=ticker_upper,
            lookback_hours=lookback_hours,
            aggregate=aggregate,
            sentiment_history=[
                SentimentMetricPoint(
                    timestamp=s.created_at,
                    label=s.label,
                    score=round(s.score, 4),
                    confidence=round(s.confidence, 4),
                    source=s.source,
                    source_weight=round(s.source_weight, 4),
                )
                for s in sentiments
            ],
            signal_history=[
                SignalMetricPoint(
                    timestamp=s.created_at,
                    signal=s.signal,
                    confidence=round(s.confidence, 4),
                    weighted_score=round(s.weighted_score, 4),
                    rationale=s.rationale,
                )
                for s in signals
            ],
        )


aggregation_service = AggregationService()
