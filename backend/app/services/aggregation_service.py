from datetime import datetime, timezone, timedelta

from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from app.models.sentiment import SentimentRecord
from app.models.signal import SignalRecord
from app.core.config import settings
from app.schemas.analytics import (
    ArticleScoreRow,
    DashboardOverviewResponse,
    EventDistributionItem,
    SentimentMetricPoint,
    SignalMetricPoint,
    TickerAggregationResponse,
    TickerArticleTableResponse,
    TickerDrilldownResponse,
    TopicClusterSummary,
    TickerMetricsResponse,
    TickerMetricSnapshot,
)
from app.models.news import NewsItem
from app.services.weighting_service import market_hours_multiplier, time_decay_multiplier
from app.services.cache_service import TtlCache


class AggregationService:
    def __init__(self) -> None:
        self._ticker_cache: TtlCache[TickerAggregationResponse] = TtlCache(
            ttl_seconds=settings.AGGREGATION_CACHE_TTL_SECONDS
        )

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _label_to_direction(label: str) -> float:
        lowered = label.lower()
        if "pos" in lowered:
            return 1.0
        if "neg" in lowered:
            return -1.0
        return 0.0

    def summarize_ticker(self, db: Session, ticker: str, lookback_hours: int = 24) -> TickerAggregationResponse:
        ticker_upper = ticker.upper()
        cache_key = f"{ticker_upper}:{lookback_hours}"
        cached = self._ticker_cache.get(cache_key)
        if cached is not None:
            return cached

        now = self._utc_now()
        start = now - timedelta(hours=lookback_hours)

        records = list(
            db.scalars(
                select(SentimentRecord).where(
                    and_(SentimentRecord.ticker == ticker_upper, SentimentRecord.created_at >= start)
                )
            )
        )

        if not records:
            payload = TickerAggregationResponse(
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
            self._ticker_cache.set(cache_key, payload)
            return payload

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

        payload = TickerAggregationResponse(
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
        self._ticker_cache.set(cache_key, payload)
        return payload

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

    def ticker_metrics(
        self,
        db: Session,
        ticker: str,
        lookback_hours: int = 72,
        bucket_hours: int = 6,
    ) -> TickerMetricsResponse:
        now = self._utc_now()
        start = now - timedelta(hours=lookback_hours)
        ticker_upper = ticker.upper()

        sentiments = list(
            db.scalars(
                select(SentimentRecord)
                .where(and_(SentimentRecord.ticker == ticker_upper, SentimentRecord.created_at >= start))
                .order_by(SentimentRecord.created_at.asc())
            )
        )

        bucket_minutes = max(bucket_hours * 60, 60)
        bucket_map: dict[datetime, list[SentimentRecord]] = {}
        for record in sentiments:
            delta_minutes = int((record.created_at - start).total_seconds() // 60)
            bucket_idx = max(delta_minutes // bucket_minutes, 0)
            bucket_start = start + timedelta(minutes=bucket_idx * bucket_minutes)
            bucket_map.setdefault(bucket_start, []).append(record)

        points: list[TickerMetricSnapshot] = []
        for bucket_start in sorted(bucket_map):
            records = bucket_map[bucket_start]
            pos_count = 0
            neu_count = 0
            neg_count = 0
            weighted_signal = 0.0
            weighted_confidence = 0.0
            total_weight = 0.0

            for record in records:
                direction = self._label_to_direction(record.label)
                if direction > 0:
                    pos_count += 1
                elif direction < 0:
                    neg_count += 1
                else:
                    neu_count += 1

                weight = record.source_weight * time_decay_multiplier(record.created_at, now=now)
                weight *= market_hours_multiplier(record.created_at)
                weighted_signal += direction * record.score * weight
                weighted_confidence += record.confidence * weight
                total_weight += weight

            total = len(records)
            score = weighted_signal / total_weight if total_weight else 0.0
            confidence = weighted_confidence / total_weight if total_weight else 0.0
            points.append(
                TickerMetricSnapshot(
                    timestamp=bucket_start,
                    article_count=total,
                    weighted_sentiment_score=round(score, 4),
                    weighted_confidence=round(confidence, 4),
                    positive_ratio=round(pos_count / total, 4),
                    neutral_ratio=round(neu_count / total, 4),
                    negative_ratio=round(neg_count / total, 4),
                )
            )

        return TickerMetricsResponse(
            ticker=ticker_upper,
            bucket_hours=bucket_hours,
            lookback_hours=lookback_hours,
            points=points,
        )

    def dashboard_overview(
        self,
        db: Session,
        lookback_hours: int = 24,
        watchlist: list[str] | None = None,
    ) -> DashboardOverviewResponse:
        now = self._utc_now()
        start = now - timedelta(hours=lookback_hours)
        sentiments = list(db.scalars(select(SentimentRecord).where(SentimentRecord.created_at >= start)))
        if not sentiments:
            return DashboardOverviewResponse(
                lookback_hours=lookback_hours,
                articles_processed=0,
                avg_sentiment_score=0.0,
                avg_confidence=0.0,
                watchlist_alerts=0,
                most_mentioned_tickers=[],
            )

        ticker_counts: dict[str, int] = {}
        for row in sentiments:
            ticker_counts[row.ticker] = ticker_counts.get(row.ticker, 0) + 1

        sorted_tickers = [item[0] for item in sorted(ticker_counts.items(), key=lambda item: item[1], reverse=True)]
        watchlist_tickers = [ticker.upper() for ticker in watchlist] if watchlist else sorted_tickers[:5]
        watchlist_alerts = 0
        for ticker in watchlist_tickers:
            aggregate = self.summarize_ticker(db, ticker=ticker, lookback_hours=lookback_hours)
            if aggregate.weighted_confidence < 0.5 or abs(aggregate.weighted_sentiment_score) > 0.4:
                watchlist_alerts += 1

        return DashboardOverviewResponse(
            lookback_hours=lookback_hours,
            articles_processed=len(sentiments),
            avg_sentiment_score=round(sum(row.score for row in sentiments) / len(sentiments), 4),
            avg_confidence=round(sum(row.confidence for row in sentiments) / len(sentiments), 4),
            watchlist_alerts=watchlist_alerts,
            most_mentioned_tickers=sorted_tickers[:10],
        )

    def event_distribution(self, db: Session, lookback_hours: int = 24) -> list[EventDistributionItem]:
        start = self._utc_now() - timedelta(hours=lookback_hours)
        rows = list(db.scalars(select(NewsItem).where(NewsItem.published_at >= start)))
        counts: dict[str, int] = {}
        for row in rows:
            counts[row.event_type] = counts.get(row.event_type, 0) + 1
        return [
            EventDistributionItem(event_type=event_type, count=count)
            for event_type, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)
        ]

    def topic_clusters(self, db: Session, lookback_hours: int = 24) -> list[TopicClusterSummary]:
        start = self._utc_now() - timedelta(hours=lookback_hours)
        rows = list(db.scalars(select(SentimentRecord).where(SentimentRecord.created_at >= start)))
        topic_keywords = {
            "earnings": {"earnings", "guidance", "revenue"},
            "macro": {"inflation", "rates", "fed", "macro"},
            "product": {"launch", "product", "platform"},
            "risk": {"risk", "volatile", "headwind"},
        }
        tracker: dict[str, dict[str, set[str] | int]] = {
            key: {"mentions": 0, "tickers": set()} for key in topic_keywords
        }
        for row in rows:
            text = row.text.lower()
            for topic, words in topic_keywords.items():
                if any(word in text for word in words):
                    tracker[topic]["mentions"] = int(tracker[topic]["mentions"]) + 1
                    casted = tracker[topic]["tickers"]
                    if isinstance(casted, set):
                        casted.add(row.ticker)
        return [
            TopicClusterSummary(
                topic=topic,
                mentions=int(data["mentions"]),
                sample_tickers=sorted(list(data["tickers"]))[:5] if isinstance(data["tickers"], set) else [],
            )
            for topic, data in tracker.items()
            if int(data["mentions"]) > 0
        ]

    def ticker_article_table(
        self,
        db: Session,
        ticker: str,
        lookback_hours: int = 72,
        limit: int = 50,
        offset: int = 0,
    ) -> TickerArticleTableResponse:
        ticker_upper = ticker.upper()
        start = self._utc_now() - timedelta(hours=lookback_hours)
        rows = list(
            db.scalars(
                select(SentimentRecord)
                .where(and_(SentimentRecord.ticker == ticker_upper, SentimentRecord.created_at >= start))
                .order_by(desc(SentimentRecord.created_at))
            )
        )
        sliced = rows[offset : offset + limit]
        return TickerArticleTableResponse(
            ticker=ticker_upper,
            lookback_hours=lookback_hours,
            total=len(rows),
            limit=limit,
            offset=offset,
            rows=[
                ArticleScoreRow(
                    sentiment_record_id=row.id,
                    ticker=row.ticker,
                    source=row.source,
                    label=row.label,
                    score=round(row.score, 4),
                    confidence=round(row.confidence, 4),
                    model_used=row.model_used,
                    timestamp=row.created_at,
                    text_preview=row.text[:180],
                )
                for row in sliced
            ],
        )


aggregation_service = AggregationService()
