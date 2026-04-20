from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import TickerAggregationResponse, TickerDrilldownResponse
from app.services.aggregation_service import aggregation_service

router = APIRouter()


@router.get("/ticker/{ticker}", response_model=TickerAggregationResponse)
def aggregate_ticker(
    ticker: str,
    lookback_hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
) -> TickerAggregationResponse:
    return aggregation_service.summarize_ticker(db, ticker=ticker, lookback_hours=lookback_hours)


@router.get("/ticker/{ticker}/drilldown", response_model=TickerDrilldownResponse)
def ticker_drilldown(
    ticker: str,
    lookback_hours: int = Query(default=72, ge=6, le=720),
    db: Session = Depends(get_db),
) -> TickerDrilldownResponse:
    return aggregation_service.ticker_drilldown(db, ticker=ticker, lookback_hours=lookback_hours)
