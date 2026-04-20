from datetime import datetime

from pydantic import BaseModel


class TickerAggregationResponse(BaseModel):
    ticker: str
    article_count: int
    avg_score: float
    avg_confidence: float
    weighted_sentiment_score: float
    weighted_confidence: float
    positive_ratio: float
    neutral_ratio: float
    negative_ratio: float
    source_breakdown: dict[str, int]
    window_start: datetime
    window_end: datetime


class SentimentMetricPoint(BaseModel):
    timestamp: datetime
    label: str
    score: float
    confidence: float
    source: str
    source_weight: float


class SignalMetricPoint(BaseModel):
    timestamp: datetime
    signal: str
    confidence: float
    weighted_score: float
    rationale: str


class TickerDrilldownResponse(BaseModel):
    ticker: str
    lookback_hours: int
    aggregate: TickerAggregationResponse
    sentiment_history: list[SentimentMetricPoint]
    signal_history: list[SignalMetricPoint]
