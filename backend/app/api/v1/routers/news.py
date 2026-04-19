import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.news import IngestNewsRequest, NewsItemResponse
from app.services.news_service import news_ingestion_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest", response_model=list[NewsItemResponse])
def ingest_news(payload: IngestNewsRequest, db: Session = Depends(get_db)) -> list[NewsItemResponse]:
    news = news_ingestion_service.ingest_mock_news(db, payload.tickers, payload.limit_per_ticker)
    logger.info("Ingested %s mock news records for tickers=%s", len(news), payload.tickers)
    return news
