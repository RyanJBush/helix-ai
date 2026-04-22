from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.trust import (
    AnnotationCreateRequest,
    AnnotationResponse,
    SignalAuditTrailResponse,
    SignalExplanationResponse,
)
from app.services.trust_service import trust_service

router = APIRouter()


@router.get("/signals/{ticker}/explanation", response_model=SignalExplanationResponse)
def explain_signal(
    ticker: str,
    lookback_hours: int = Query(default=24, ge=1, le=168),
    top_n: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> SignalExplanationResponse:
    return trust_service.explain_signal(db, ticker=ticker, lookback_hours=lookback_hours, top_n=top_n)


@router.post("/annotations", response_model=AnnotationResponse)
def create_annotation(payload: AnnotationCreateRequest, db: Session = Depends(get_db)) -> AnnotationResponse:
    return trust_service.create_annotation(db, payload)


@router.get("/annotations/{ticker}", response_model=list[AnnotationResponse])
def list_annotations(
    ticker: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0, le=10000),
    db: Session = Depends(get_db),
) -> list[AnnotationResponse]:
    return trust_service.list_annotations(db, ticker=ticker, limit=limit, offset=offset)


@router.get("/signals/{ticker}/audit", response_model=SignalAuditTrailResponse)
def signal_audit(
    ticker: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> SignalAuditTrailResponse:
    return trust_service.signal_audit_trail(db, ticker=ticker, limit=limit)
