from datetime import datetime

from pydantic import BaseModel, Field


class TickerBriefingResponse(BaseModel):
    ticker: str
    summary: str
    key_topics: list[str]
    key_events: list[str]
    confidence_note: str
    generated_at: datetime


class WatchlistRecapRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=30)
    lookback_hours: int = Field(default=24, ge=1, le=168)


class WatchlistRecapResponse(BaseModel):
    generated_at: datetime
    recap: str
    tickers: list[str]
