from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.news import IngestNewsRequest
from app.schemas.sentiment import SentimentRequest


JobType = Literal["ingestion", "sentiment_batch"]
JobStatus = Literal["queued", "running", "completed", "failed"]


class JobResponse(BaseModel):
    job_id: str
    job_type: JobType
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    records_processed: int = 0
    error_message: str | None = None


class SentimentBatchJobRequest(BaseModel):
    items: list[SentimentRequest] = Field(..., min_length=1, max_length=100)


class IngestionJobRequest(BaseModel):
    payload: IngestNewsRequest
