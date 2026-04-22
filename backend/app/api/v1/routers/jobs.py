from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from app.core.middleware import enforce_rate_limit
from app.db.session import get_db
from app.schemas.jobs import IngestionJobRequest, JobResponse, SentimentBatchJobRequest
from app.services.job_service import job_service
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/ingestion", response_model=JobResponse)
def queue_ingestion_job(
    payload: IngestionJobRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> JobResponse:
    enforce_rate_limit(request)
    job_id = job_service.create_job("ingestion")
    background_tasks.add_task(job_service.run_ingestion_job, job_id, payload.payload, db)
    status = job_service.get_job(job_id)
    if status is None:
        raise HTTPException(status_code=500, detail="Failed to create ingestion job")
    return status


@router.post("/sentiment-batch", response_model=JobResponse)
def queue_sentiment_batch_job(
    payload: SentimentBatchJobRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> JobResponse:
    enforce_rate_limit(request)
    job_id = job_service.create_job("sentiment_batch")
    background_tasks.add_task(job_service.run_sentiment_batch_job, job_id, payload.items, db)
    status = job_service.get_job(job_id)
    if status is None:
        raise HTTPException(status_code=500, detail="Failed to create sentiment job")
    return status


@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str) -> JobResponse:
    status = job_service.get_job(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status
