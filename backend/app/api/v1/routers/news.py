import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.middleware import enforce_rate_limit
from app.db.session import get_db
from app.models.sentiment import SentimentRecord
from app.models.signal import SignalRecord
from app.schemas.news import IngestAndScoreResponse, IngestNewsRequest, IngestionRunResponse, NewsItemResponse
from app.schemas.sentiment import SentimentRequest
from app.services.aggregation_service import aggregation_service
from app.services.news_service import news_ingestion_service
from app.services.nlp_service import nlp_service
from app.services.signal_service import signal_service
from app.services.weighting_service import get_source_weight

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest", response_model=list[NewsItemResponse])
def ingest_news(
    payload: IngestNewsRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> list[NewsItemResponse]:
    enforce_rate_limit(request)
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


@router.post("/ingest-and-score", response_model=IngestAndScoreResponse)
def ingest_and_score(
    payload: IngestNewsRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> IngestAndScoreResponse:
    enforce_rate_limit(request)
    result = news_ingestion_service.ingest_news(db, payload)
    sentiments_created = 0
    signals_created = 0
    impacted_tickers = sorted({item.ticker.upper() for item in result.items})

    for item in result.items:
        sentiment = nlp_service.analyze_sentiment(
            SentimentRequest(
                ticker=item.ticker,
                source=item.source_type,
                headline=item.headline,
                body=item.content,
                news_item_id=item.id,
            )
        )
        db.add(
            SentimentRecord(
                ticker=sentiment.ticker,
                source=item.source_type,
                news_item_id=item.id,
                text=f"{item.headline} {item.content}".strip(),
                score=sentiment.score,
                confidence=sentiment.confidence,
                source_weight=get_source_weight(item.source_type),
                model_used=sentiment.model_used,
                label=sentiment.label,
            )
        )
        sentiments_created += 1

    db.commit()
    aggregation_service._ticker_cache.clear()

    for ticker in impacted_tickers:
        aggregate = aggregation_service.summarize_ticker(db, ticker=ticker, lookback_hours=payload.lookback_days * 24)
        signal = signal_service.generate_from_aggregate(aggregate)
        db.add(
            SignalRecord(
                ticker=signal.ticker,
                signal=signal.signal,
                confidence=signal.confidence,
                weighted_score=signal.weighted_score,
                buy_threshold=signal.buy_threshold,
                sell_threshold=signal.sell_threshold,
                min_confidence=signal.min_confidence,
                rationale=signal.rationale,
            )
        )
        signals_created += 1
    db.commit()

    return IngestAndScoreResponse(
        run_id=result.run_id,
        tickers=impacted_tickers,
        news_items_inserted=len(result.items),
        sentiments_created=sentiments_created,
        signals_created=signals_created,
    )
