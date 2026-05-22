from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sentiment import SentimentRecord
from app.models.watchlist import MarketCapSnapshot, Watchlist
from app.schemas.portfolio import (
    FearGreedResponse,
    TickerSentimentBreakdown,
    WatchlistCreateRequest,
    WatchlistResponse,
    WatchlistSentimentResponse,
)
from app.services.fear_greed import fear_greed_service

router = APIRouter()


@router.post('/watchlists', response_model=WatchlistResponse)
def create_watchlist(payload: WatchlistCreateRequest, db: Session = Depends(get_db)) -> WatchlistResponse:
    wl = Watchlist(name=payload.name, owner=payload.owner, tickers_csv=','.join(t.upper() for t in payload.tickers))
    db.add(wl)
    db.commit()
    db.refresh(wl)
    return WatchlistResponse(id=wl.id, name=wl.name, owner=wl.owner, tickers=[t.strip() for t in wl.tickers_csv.split(',') if t.strip()], created_at=wl.created_at)


@router.get('/watchlists/{watchlist_id}/sentiment', response_model=WatchlistSentimentResponse)
def watchlist_sentiment(watchlist_id: int, db: Session = Depends(get_db)) -> WatchlistSentimentResponse:
    wl = db.get(Watchlist, watchlist_id)
    if not wl:
        raise HTTPException(status_code=404, detail='Watchlist not found')

    tickers = [t.strip().upper() for t in wl.tickers_csv.split(',') if t.strip()]
    since = datetime.utcnow() - timedelta(hours=24)
    breakdown: list[TickerSentimentBreakdown] = []
    weighted_num = 0.0
    weighted_den = 0.0

    for ticker in tickers:
      vals = [r.score for r in db.scalars(select(SentimentRecord).where(SentimentRecord.ticker == ticker, SentimentRecord.created_at >= since))]
      avg = (sum(vals) / len(vals)) if vals else 0.0
      cap = db.scalar(select(MarketCapSnapshot.market_cap).where(MarketCapSnapshot.ticker == ticker).order_by(desc(MarketCapSnapshot.observed_at)).limit(1))
      weighted = avg if cap is None else avg * cap
      breakdown.append(TickerSentimentBreakdown(ticker=ticker, avg_sentiment=round(avg, 4), market_cap=cap, weighted_sentiment=round(weighted, 4) if cap is not None else None))
      if cap is not None:
          weighted_num += avg * cap
          weighted_den += cap

    simple_avg = sum(item.avg_sentiment for item in breakdown) / len(breakdown) if breakdown else 0.0
    weighted_avg = (weighted_num / weighted_den) if weighted_den > 0 else None
    return WatchlistSentimentResponse(watchlist_id=wl.id, name=wl.name, simple_average_sentiment=round(simple_avg, 4), market_cap_weighted_sentiment=round(weighted_avg, 4) if weighted_avg is not None else None, breakdown=breakdown)


@router.get('/market/fear-greed', response_model=FearGreedResponse)
def fear_greed(db: Session = Depends(get_db)) -> FearGreedResponse:
    return FearGreedResponse(**fear_greed_service.compute(db))
