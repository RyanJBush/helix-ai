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
    next_day_return: float
    intraday_move: float
    volatility_change: float
    benchmark_return: float
    relative_return: float


class ConfusionMatrix(BaseModel):
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int


class BacktestResponse(BaseModel):
    ticker: str
    period_start: date
    period_end: date
    total_days: int
    trade_days: int
    hit_rate: float
    precision: float
    recall: float
    cumulative_proxy_return: float
    cumulative_benchmark_return: float
    cumulative_relative_return: float
    max_drawdown: float
    sharpe_like_ratio: float
    return_correlation: float
    avg_return_per_trade: float
    expectancy: float
    long_hit_rate: float
    short_hit_rate: float
    assumptions: list[str]
    confusion_matrix: ConfusionMatrix
    results: list[BacktestDayResult]


class ThresholdTuningRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    start_date: date
    end_date: date
    buy_thresholds: list[float] = Field(default=[0.15, 0.2, 0.25, 0.3], min_length=1, max_length=12)
    sell_thresholds: list[float] = Field(default=[-0.15, -0.2, -0.25, -0.3], min_length=1, max_length=12)
    min_confidences: list[float] = Field(default=[0.35, 0.45, 0.55], min_length=1, max_length=6)


class ThresholdCandidate(BaseModel):
    buy_threshold: float
    sell_threshold: float
    min_confidence: float
    sharpe_like_ratio: float
    hit_rate: float
    cumulative_proxy_return: float


class ThresholdTuningResponse(BaseModel):
    ticker: str
    tested_candidates: int
    best_candidate: ThresholdCandidate
    leaderboard: list[ThresholdCandidate]


class PaperTradeRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    start_date: date
    end_date: date
    initial_cash: float = Field(default=10000.0, gt=0)
    position_size: float = Field(default=0.2, gt=0, le=1)
    buy_threshold: float = 0.25
    sell_threshold: float = -0.25
    min_confidence: float = Field(default=0.45, ge=0, le=1)


class PaperTradeDay(BaseModel):
    date: date
    signal: str
    cash: float
    position_units: float
    mark_price: float
    portfolio_value: float


class PaperTradeResponse(BaseModel):
    ticker: str
    initial_cash: float
    final_cash: float
    final_portfolio_value: float
    total_trades: int
    days: list[PaperTradeDay]


class ScenarioBacktestResult(BaseModel):
    scenario: str
    buy_threshold: float
    sell_threshold: float
    min_confidence: float
    hit_rate: float
    sharpe_like_ratio: float
    cumulative_proxy_return: float
    cumulative_relative_return: float


class ScenarioBacktestResponse(BaseModel):
    ticker: str
    period_start: date
    period_end: date
    scenarios: list[ScenarioBacktestResult]
