from datetime import datetime

from pydantic import BaseModel, Field


class SignalContributor(BaseModel):
    sentiment_record_id: int
    source: str
    label: str
    score: float
    confidence: float
    contribution_weight: float


class SourceContradiction(BaseModel):
    source: str
    positive_count: int
    negative_count: int


class SignalExplanationResponse(BaseModel):
    ticker: str
    lookback_hours: int
    generated_signal: str
    generated_confidence: float
    confidence_disclaimer: str | None
    top_contributors: list[SignalContributor]
    contradictions: list[SourceContradiction]
    generated_at: datetime


class AnnotationCreateRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    note: str = Field(..., min_length=3, max_length=2000)
    author: str = Field(default="analyst", min_length=2, max_length=64)
    signal_record_id: int | None = None


class AnnotationResponse(BaseModel):
    id: int
    ticker: str
    note: str
    author: str
    signal_record_id: int | None
    created_at: datetime


class SignalAuditEntry(BaseModel):
    id: int
    signal: str
    confidence: float
    weighted_score: float
    rationale: str
    created_at: datetime


class SignalAuditTrailResponse(BaseModel):
    ticker: str
    entries: list[SignalAuditEntry]
