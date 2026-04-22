from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class IngestNewsRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=10)
    limit_per_ticker: int = Field(default=3, ge=1, le=10)
    sources: list[str] = Field(
        default=["financial_news", "press_release", "earnings_wire", "social_curated"],
        min_length=1,
        max_length=6,
    )
    mode: Literal["realtime", "historical_backfill"] = "realtime"
    lookback_days: int = Field(default=14, ge=1, le=180)


class NewsItemResponse(BaseModel):
    id: int
    ticker: str
    source: str
    source_type: str
    source_weight: float
    event_type: str
    market_session: str
    related_tickers: list[str]
    headline: str
    content: str
    published_at: datetime
    ingested_at: datetime


class IngestionRunResponse(BaseModel):
    id: int
    status: str
    mode: str
    requested_tickers: list[str]
    requested_sources: list[str]
    records_inserted: int
    duplicates_skipped: int
    failures_count: int
    source_stats: dict[str, int]
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None
