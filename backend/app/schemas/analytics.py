from datetime import datetime

from pydantic import BaseModel


class TickerAggregationResponse(BaseModel):
    ticker: str
    article_count: int
    avg_score: float
    positive_ratio: float
    neutral_ratio: float
    negative_ratio: float
    window_start: datetime
    window_end: datetime
