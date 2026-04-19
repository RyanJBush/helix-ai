import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.signal import SignalRecord
from app.schemas.sentiment import SignalResponse
from app.services.aggregation_service import aggregation_service
from app.services.signal_service import signal_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/ticker/{ticker}", response_model=SignalResponse)
def generate_signal(ticker: str, db: Session = Depends(get_db)) -> SignalResponse:
    aggregate = aggregation_service.summarize_ticker(db, ticker=ticker)
    signal = signal_service.generate_from_aggregate(aggregate)

    db_record = SignalRecord(
        ticker=signal.ticker,
        signal=signal.signal,
        confidence=signal.confidence,
        rationale=signal.rationale,
    )
    db.add(db_record)
    db.commit()

    logger.info("Signal generated for %s signal=%s confidence=%.3f", signal.ticker, signal.signal, signal.confidence)
    return signal
