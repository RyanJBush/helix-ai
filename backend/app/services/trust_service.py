from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from app.models.annotation import AnalystAnnotation
from app.models.sentiment import SentimentRecord
from app.models.signal import SignalRecord
from app.schemas.trust import (
    AnnotationCreateRequest,
    AnnotationResponse,
    SignalAuditEntry,
    SignalAuditTrailResponse,
    SignalContributor,
    SignalExplanationResponse,
    SourceContradiction,
)
from app.services.aggregation_service import aggregation_service
from app.services.signal_service import signal_service
from app.services.weighting_service import market_hours_multiplier, time_decay_multiplier


class TrustService:
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _label_to_direction(label: str) -> float:
        lower = label.lower()
        if "pos" in lower:
            return 1.0
        if "neg" in lower:
            return -1.0
        return 0.0

    def explain_signal(self, db: Session, ticker: str, lookback_hours: int = 24, top_n: int = 5) -> SignalExplanationResponse:
        ticker_upper = ticker.upper()
        aggregate = aggregation_service.summarize_ticker(db, ticker=ticker_upper, lookback_hours=lookback_hours)
        signal = signal_service.generate_from_aggregate(aggregate)

        start = self._utc_now() - timedelta(hours=lookback_hours)
        rows = list(
            db.scalars(
                select(SentimentRecord)
                .where(and_(SentimentRecord.ticker == ticker_upper, SentimentRecord.created_at >= start))
                .order_by(desc(SentimentRecord.created_at))
            )
        )

        now = self._utc_now()
        contributors: list[SignalContributor] = []
        contradiction_map: dict[str, dict[str, int]] = {}
        for row in rows:
            direction = self._label_to_direction(row.label)
            weight = row.source_weight * market_hours_multiplier(row.created_at) * time_decay_multiplier(row.created_at, now=now)
            contributors.append(
                SignalContributor(
                    sentiment_record_id=row.id,
                    source=row.source,
                    label=row.label,
                    score=round(row.score, 4),
                    confidence=round(row.confidence, 4),
                    contribution_weight=round(abs(direction * row.score * weight), 4),
                )
            )
            source_bucket = contradiction_map.setdefault(row.source, {"positive": 0, "negative": 0})
            if direction > 0:
                source_bucket["positive"] += 1
            if direction < 0:
                source_bucket["negative"] += 1

        top_contributors = sorted(contributors, key=lambda item: item.contribution_weight, reverse=True)[:top_n]
        contradictions = [
            SourceContradiction(
                source=source,
                positive_count=counts["positive"],
                negative_count=counts["negative"],
            )
            for source, counts in contradiction_map.items()
            if counts["positive"] > 0 and counts["negative"] > 0
        ]
        disclaimer = None
        if signal.confidence < 0.55:
            disclaimer = "Low confidence signal: interpret with caution and corroborate with price/volume context."

        return SignalExplanationResponse(
            ticker=ticker_upper,
            lookback_hours=lookback_hours,
            generated_signal=signal.signal,
            generated_confidence=signal.confidence,
            confidence_disclaimer=disclaimer,
            top_contributors=top_contributors,
            contradictions=contradictions,
            generated_at=self._utc_now(),
        )

    def create_annotation(self, db: Session, payload: AnnotationCreateRequest) -> AnnotationResponse:
        row = AnalystAnnotation(
            ticker=payload.ticker.upper(),
            note=payload.note,
            author=payload.author,
            signal_record_id=payload.signal_record_id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return AnnotationResponse(
            id=row.id,
            ticker=row.ticker,
            note=row.note,
            author=row.author,
            signal_record_id=row.signal_record_id,
            created_at=row.created_at,
        )

    def list_annotations(self, db: Session, ticker: str, limit: int = 50, offset: int = 0) -> list[AnnotationResponse]:
        rows = list(
            db.scalars(
                select(AnalystAnnotation)
                .where(AnalystAnnotation.ticker == ticker.upper())
                .order_by(desc(AnalystAnnotation.created_at))
                .offset(offset)
                .limit(limit)
            )
        )
        return [
            AnnotationResponse(
                id=row.id,
                ticker=row.ticker,
                note=row.note,
                author=row.author,
                signal_record_id=row.signal_record_id,
                created_at=row.created_at,
            )
            for row in rows
        ]

    def signal_audit_trail(self, db: Session, ticker: str, limit: int = 50) -> SignalAuditTrailResponse:
        rows = list(
            db.scalars(
                select(SignalRecord)
                .where(SignalRecord.ticker == ticker.upper())
                .order_by(desc(SignalRecord.created_at))
                .limit(limit)
            )
        )
        return SignalAuditTrailResponse(
            ticker=ticker.upper(),
            entries=[
                SignalAuditEntry(
                    id=row.id,
                    signal=row.signal,
                    confidence=round(row.confidence, 4),
                    weighted_score=round(row.weighted_score, 4),
                    rationale=row.rationale,
                    created_at=row.created_at,
                )
                for row in rows
            ],
        )


trust_service = TrustService()
