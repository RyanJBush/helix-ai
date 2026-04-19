from datetime import datetime

from pydantic import BaseModel, Field


class SentimentRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    text: str = Field(..., min_length=3, max_length=4096)
    source: str = Field(default="news", min_length=2, max_length=64)


class SentimentResponse(BaseModel):
    ticker: str
    label: str
    score: float
    processed_at: datetime


class SignalResponse(BaseModel):
    ticker: str
    signal: str
    confidence: float
    rationale: str
    generated_at: datetime
