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


class TickerMetricSnapshot(BaseModel):
    timestamp: datetime
    article_count: int
    weighted_sentiment_score: float
    weighted_confidence: float
    positive_ratio: float
    neutral_ratio: float
    negative_ratio: float


class TickerDrilldownResponse(BaseModel):
    ticker: str
    lookback_hours: int
    aggregate: TickerAggregationResponse
    sentiment_history: list[SentimentMetricPoint]
    signal_history: list[SignalMetricPoint]


class TickerMetricsResponse(BaseModel):
    ticker: str
    bucket_hours: int
    lookback_hours: int
    points: list[TickerMetricSnapshot]


class EventDistributionItem(BaseModel):
    event_type: str
    count: int


class TopicClusterSummary(BaseModel):
    topic: str
    mentions: int
    sample_tickers: list[str]


class DashboardOverviewResponse(BaseModel):
    lookback_hours: int
    articles_processed: int
    avg_sentiment_score: float
    avg_confidence: float
    watchlist_alerts: int
    most_mentioned_tickers: list[str]


class ArticleScoreRow(BaseModel):
    sentiment_record_id: int
    ticker: str
    source: str
    label: str
    score: float
    confidence: float
    model_used: str
    timestamp: datetime
    text_preview: str


class TickerArticleTableResponse(BaseModel):
    ticker: str
    lookback_hours: int
    total: int
    limit: int
    offset: int
    rows: list[ArticleScoreRow]
