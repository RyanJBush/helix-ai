import logging

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sentiment import SentimentRecord
from app.schemas.sentiment import SentimentRequest, SentimentResponse
from app.services.nlp_service import nlp_service
from app.services.stream_service import stream_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=SentimentResponse)
def analyze(
    payload: SentimentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> SentimentResponse:
    result = nlp_service.analyze_sentiment(payload)

    db_record = SentimentRecord(
        ticker=result.ticker,
        source=payload.source,
        text=payload.text,
        score=result.score,
        label=result.label,
    )
    db.add(db_record)
    db.commit()

    background_tasks.add_task(
        stream_manager.broadcast,
        {
            "event": "sentiment_update",
            "ticker": result.ticker,
            "label": result.label,
            "score": result.score,
            "processed_at": result.processed_at.isoformat(),
        },
    )

    logger.info("Sentiment analyzed for %s label=%s score=%.3f", result.ticker, result.label, result.score)
    return result
