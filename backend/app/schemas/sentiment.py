from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class SentimentRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    text: str | None = Field(default=None, min_length=3, max_length=4096)
    headline: str | None = Field(default=None, min_length=3, max_length=512)
    body: str | None = Field(default=None, min_length=3, max_length=4096)
    source: str = Field(default="news", min_length=2, max_length=64)
    news_item_id: int | None = None
    compare_models: bool = False

    @model_validator(mode="after")
    def validate_content_fields(self) -> "SentimentRequest":
        if not self.text and not self.headline and not self.body:
            raise ValueError("One of text, headline, or body must be provided")
        return self


class ModelComparison(BaseModel):
    baseline_label: str
    baseline_score: float
    advanced_label: str
    advanced_score: float
    absolute_score_delta: float


class SentimentResponse(BaseModel):
    ticker: str
    label: str
    score: float
    headline_score: float
    body_score: float
    confidence: float
    entity_sentiment: dict[str, float]
    topics: list[str]
    events: list[str]
    cluster_id: str
    model_used: str
    model_comparison: ModelComparison | None = None
    processed_at: datetime


class SignalResponse(BaseModel):
    ticker: str
    signal: str
    confidence: float
    weighted_score: float
    buy_threshold: float
    sell_threshold: float
    min_confidence: float
    signal_strength: float
    factors: dict[str, float]
    alert: str | None = None
    rationale: str
    generated_at: datetime


class WatchlistSignalRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=30)
    buy_threshold: float = 0.25
    sell_threshold: float = -0.25
    min_confidence: float = 0.45
    lookback_hours: int = Field(default=24, ge=1, le=168)


class WatchlistSignalResponse(BaseModel):
    generated_at: datetime
    signals: list[SignalResponse]


class WatchlistAlert(BaseModel):
    ticker: str
    signal: str
    alert_type: str
    confidence: float
    detail: str


class WatchlistAlertResponse(BaseModel):
    generated_at: datetime
    alerts: list[WatchlistAlert]
