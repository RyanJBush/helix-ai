from datetime import date

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    start_date: date
    end_date: date
    buy_threshold: float = 0.25
    sell_threshold: float = -0.25
    min_confidence: float = Field(default=0.45, ge=0.0, le=1.0)


class BacktestDayResult(BaseModel):
    date: date
    weighted_sentiment_score: float
    weighted_confidence: float
    signal: str
    proxy_return: float


class BacktestResponse(BaseModel):
    ticker: str
    period_start: date
    period_end: date
    total_days: int
    trade_days: int
    hit_rate: float
    cumulative_proxy_return: float
    sharpe_like_ratio: float
    results: list[BacktestDayResult]
