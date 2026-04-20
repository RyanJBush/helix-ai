import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.signal import SignalRecord
from app.schemas.sentiment import SignalResponse
from app.services.aggregation_service import aggregation_service
from app.services.signal_service import SignalThresholds, signal_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/ticker/{ticker}", response_model=SignalResponse)
def generate_signal(
    ticker: str,
    buy_threshold: float = Query(default=settings.DEFAULT_BUY_THRESHOLD, ge=0.0, le=1.0),
    sell_threshold: float = Query(default=settings.DEFAULT_SELL_THRESHOLD, ge=-1.0, le=0.0),
    min_confidence: float = Query(default=settings.DEFAULT_MIN_SIGNAL_CONFIDENCE, ge=0.0, le=1.0),
    lookback_hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
) -> SignalResponse:
    thresholds = SignalThresholds(
        buy_threshold=buy_threshold,
        sell_threshold=sell_threshold,
        min_confidence=min_confidence,
    )
    aggregate = aggregation_service.summarize_ticker(db, ticker=ticker, lookback_hours=lookback_hours)
    signal = signal_service.generate_from_aggregate(aggregate, thresholds=thresholds)

    db_record = SignalRecord(
        ticker=signal.ticker,
        signal=signal.signal,
        confidence=signal.confidence,
        weighted_score=signal.weighted_score,
        buy_threshold=signal.buy_threshold,
        sell_threshold=signal.sell_threshold,
        min_confidence=signal.min_confidence,
        rationale=signal.rationale,
    )
    db.add(db_record)
    db.commit()

    logger.info("Signal generated for %s signal=%s confidence=%.3f", signal.ticker, signal.signal, signal.confidence)
    return signal
