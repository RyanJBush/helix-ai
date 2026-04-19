from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class NewsArticleIn(BaseModel):
    ticker: str = Field(min_length=1, max_length=8)
    source: str = Field(default="simulated", min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


class NewsArticle(NewsArticleIn):
    id: str
    created_at: datetime


class IngestRequest(BaseModel):
    articles: list[NewsArticleIn] = Field(default_factory=list)
    simulate_count: int = Field(default=0, ge=0, le=25)


class SentimentRecord(BaseModel):
    article_id: str
    ticker: str
    score: float
    label: Literal["positive", "neutral", "negative"]
    created_at: datetime


class AggregatedSentiment(BaseModel):
    ticker: str
    average_score: float
    label: Literal["positive", "neutral", "negative"]
    sample_size: int
    updated_at: datetime


class TradingSignal(BaseModel):
    ticker: str
    signal: Literal["BUY", "HOLD", "SELL"]
    confidence: float
    reason: str
    updated_at: datetime


class AnalyzeRequest(BaseModel):
    ticker: str | None = None


class DashboardSummary(BaseModel):
    total_articles: int
    analyzed_articles: int
    tracked_tickers: int
    bullish_tickers: int
    bearish_tickers: int
