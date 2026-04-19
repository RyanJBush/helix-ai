from datetime import datetime

from pydantic import BaseModel, Field


class IngestNewsRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=10)
    limit_per_ticker: int = Field(default=3, ge=1, le=10)


class NewsItemResponse(BaseModel):
    ticker: str
    source: str
    headline: str
    content: str
    published_at: datetime
