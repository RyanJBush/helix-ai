import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.news import IngestNewsRequest, IngestionRunResponse, NewsItemResponse
from app.services.news_service import news_ingestion_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest", response_model=list[NewsItemResponse])
def ingest_news(payload: IngestNewsRequest, response: Response, db: Session = Depends(get_db)) -> list[NewsItemResponse]:
    result = news_ingestion_service.ingest_news(db, payload)
    response.headers["X-Ingestion-Run-Id"] = str(result.run_id)
    logger.info("Ingested %s news records for tickers=%s", len(result.items), payload.tickers)
    return result.items


@router.get("/ingest/status/latest", response_model=IngestionRunResponse)
def latest_ingest_status(db: Session = Depends(get_db)) -> IngestionRunResponse:
    status = news_ingestion_service.latest_run_status(db)
    if status is None:
        raise HTTPException(status_code=404, detail="No ingestion runs found")
    return status


@router.get("/ingest/status/{run_id}", response_model=IngestionRunResponse)
def ingest_status(run_id: int, db: Session = Depends(get_db)) -> IngestionRunResponse:
    status = news_ingestion_service.get_run_status(db, run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return status
