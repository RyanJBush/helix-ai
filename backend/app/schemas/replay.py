from datetime import datetime

from pydantic import BaseModel, Field


class ReplayRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=20)
    steps: int = Field(default=5, ge=1, le=50)
    seed: int = 42


class ReplayEvent(BaseModel):
    ticker: str
    step: int
    label: str
    score: float
    confidence: float
    signal: str


class ReplayResponse(BaseModel):
    generated_at: datetime
    events: list[ReplayEvent]
