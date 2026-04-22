from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.briefing import TickerBriefingResponse, WatchlistRecapRequest, WatchlistRecapResponse
from app.services.briefing_service import briefing_service

router = APIRouter()


@router.get("/ticker/{ticker}", response_model=TickerBriefingResponse)
def ticker_briefing(
    ticker: str,
    lookback_hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
) -> TickerBriefingResponse:
    return briefing_service.ticker_briefing(db, ticker=ticker, lookback_hours=lookback_hours)


@router.post("/watchlist", response_model=WatchlistRecapResponse)
def watchlist_recap(payload: WatchlistRecapRequest, db: Session = Depends(get_db)) -> WatchlistRecapResponse:
    return briefing_service.watchlist_recap(db, payload)
