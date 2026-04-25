import logging

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.middleware import enforce_rate_limit
from app.db.session import get_db
from app.models.signal import SignalRecord
from app.schemas.sentiment import (
    SignalResponse,
    WatchlistAlert,
    WatchlistAlertResponse,
    WatchlistSignalRequest,
    WatchlistSignalResponse,
)
from app.services.aggregation_service import aggregation_service
from app.services.signal_service import SignalContext, SignalRuntimeConfig, SignalThresholds, signal_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/ticker/{ticker}", response_model=SignalResponse)
def generate_signal(
    ticker: str,
    request: Request,
    buy_threshold: float = Query(default=settings.DEFAULT_BUY_THRESHOLD, ge=0.0, le=1.0),
    sell_threshold: float = Query(default=settings.DEFAULT_SELL_THRESHOLD, ge=-1.0, le=0.0),
    min_confidence: float = Query(default=settings.DEFAULT_MIN_SIGNAL_CONFIDENCE, ge=0.0, le=1.0),
    lookback_hours: int = Query(default=24, ge=1, le=168),
    event_impact: float = Query(default=0.0, ge=-1.0, le=1.0),
    volume_zscore: float = Query(default=0.0, ge=-3.0, le=3.0),
    price_momentum: float = Query(default=0.0, ge=-1.0, le=1.0),
    watchlist_priority: float = Query(default=0.0, ge=0.0, le=1.0),
    cooldown_minutes: int = Query(default=30, ge=5, le=240),
    sharp_shift_delta: float = Query(default=0.45, ge=0.1, le=1.5),
    db: Session = Depends(get_db),
) -> SignalResponse:
    enforce_rate_limit(request)
    thresholds = SignalThresholds(
        buy_threshold=buy_threshold,
        sell_threshold=sell_threshold,
        min_confidence=min_confidence,
    )
    aggregate = aggregation_service.summarize_ticker(db, ticker=ticker, lookback_hours=lookback_hours)
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=cooldown_minutes)
    recent = list(
        db.scalars(
            select(SignalRecord.signal)
            .where(and_(SignalRecord.ticker == ticker.upper(), SignalRecord.created_at >= cutoff))
            .order_by(desc(SignalRecord.created_at))
            .limit(1)
        )
    )
    signal = signal_service.generate_from_aggregate(
        aggregate,
        thresholds=thresholds,
        context=SignalContext(
            event_impact=event_impact,
            volume_zscore=volume_zscore,
            price_momentum=price_momentum,
            watchlist_priority=watchlist_priority,
        ),
        recent_signals=recent,
        runtime=SignalRuntimeConfig(cooldown_minutes=cooldown_minutes, sharp_shift_delta=sharp_shift_delta),
    )

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


@router.post("/watchlist", response_model=WatchlistSignalResponse)
def generate_watchlist_signals(
    payload: WatchlistSignalRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> WatchlistSignalResponse:
    enforce_rate_limit(request)
    responses: list[SignalResponse] = []
    for ticker in [ticker.upper() for ticker in payload.tickers]:
        aggregate = aggregation_service.summarize_ticker(db, ticker=ticker, lookback_hours=payload.lookback_hours)
        signal = signal_service.generate_from_aggregate(
            aggregate,
            thresholds=SignalThresholds(
                buy_threshold=payload.buy_threshold,
                sell_threshold=payload.sell_threshold,
                min_confidence=payload.min_confidence,
            ),
            context=SignalContext(watchlist_priority=1.0),
        )
        responses.append(signal)

    return WatchlistSignalResponse(generated_at=datetime.utcnow(), signals=responses)


@router.get("/watchlist/alerts", response_model=WatchlistAlertResponse)
def watchlist_alerts(
    tickers: list[str] = Query(..., min_length=1, max_length=30),
    lookback_hours: int = Query(default=24, ge=1, le=168),
    request: Request = None,
    db: Session = Depends(get_db),
) -> WatchlistAlertResponse:
    if request is not None:
        enforce_rate_limit(request)
    alerts: list[WatchlistAlert] = []
    for ticker in [value.upper() for value in tickers]:
        aggregate = aggregation_service.summarize_ticker(db, ticker=ticker, lookback_hours=lookback_hours)
        signal = signal_service.generate_from_aggregate(aggregate)
        if signal.alert:
            severity = "high" if signal.confidence >= 0.65 else "medium"
            alerts.append(
                WatchlistAlert(
                    ticker=ticker,
                    signal=signal.signal,
                    alert_type=signal.alert,
                    severity=severity,
                    confidence=signal.confidence,
                    detail=signal.rationale,
                )
            )
        elif signal.confidence < 0.5:
            severity = "high" if signal.confidence < 0.35 else "medium"
            alerts.append(
                WatchlistAlert(
                    ticker=ticker,
                    signal=signal.signal,
                    alert_type="low_confidence",
                    severity=severity,
                    confidence=signal.confidence,
                    detail="Signal confidence below 0.50; monitoring only.",
                )
            )
        elif signal.signal in {"BUY", "SELL"} and abs(signal.weighted_score) >= 0.45:
            alerts.append(
                WatchlistAlert(
                    ticker=ticker,
                    signal=signal.signal,
                    alert_type="strong_directional_signal",
                    severity="low",
                    confidence=signal.confidence,
                    detail="Directional signal crossed strong score threshold.",
                )
            )
    return WatchlistAlertResponse(generated_at=datetime.utcnow(), alerts=alerts)
