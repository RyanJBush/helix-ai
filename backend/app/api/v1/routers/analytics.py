from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import (
    DashboardOverviewResponse,
    EventDistributionItem,
    TickerAggregationResponse,
    TickerArticleTableResponse,
    TickerDrilldownResponse,
    TickerMetricsResponse,
    TopicClusterSummary,
)
from app.services.aggregation_service import aggregation_service

router = APIRouter()


@router.get("/ticker/{ticker}", response_model=TickerAggregationResponse)
def aggregate_ticker(
    ticker: str,
    lookback_hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
) -> TickerAggregationResponse:
    return aggregation_service.summarize_ticker(db, ticker=ticker, lookback_hours=lookback_hours)


@router.get("/ticker/{ticker}/drilldown", response_model=TickerDrilldownResponse)
def ticker_drilldown(
    ticker: str,
    lookback_hours: int = Query(default=72, ge=6, le=720),
    db: Session = Depends(get_db),
) -> TickerDrilldownResponse:
    return aggregation_service.ticker_drilldown(db, ticker=ticker, lookback_hours=lookback_hours)


@router.get("/ticker/{ticker}/metrics", response_model=TickerMetricsResponse)
def ticker_metrics(
    ticker: str,
    lookback_hours: int = Query(default=72, ge=6, le=720),
    bucket_hours: int = Query(default=6, ge=1, le=24),
    db: Session = Depends(get_db),
) -> TickerMetricsResponse:
    return aggregation_service.ticker_metrics(
        db,
        ticker=ticker,
        lookback_hours=lookback_hours,
        bucket_hours=bucket_hours,
    )


@router.get("/overview", response_model=DashboardOverviewResponse)
def dashboard_overview(
    lookback_hours: int = Query(default=24, ge=1, le=168),
    watchlist: list[str] | None = Query(default=None),
    db: Session = Depends(get_db),
) -> DashboardOverviewResponse:
    return aggregation_service.dashboard_overview(db, lookback_hours=lookback_hours, watchlist=watchlist)


@router.get("/events/distribution", response_model=list[EventDistributionItem])
def event_distribution(
    lookback_hours: int = Query(default=72, ge=1, le=720),
    db: Session = Depends(get_db),
) -> list[EventDistributionItem]:
    return aggregation_service.event_distribution(db, lookback_hours=lookback_hours)


@router.get("/topics/clusters", response_model=list[TopicClusterSummary])
def topic_clusters(
    lookback_hours: int = Query(default=72, ge=1, le=720),
    db: Session = Depends(get_db),
) -> list[TopicClusterSummary]:
    return aggregation_service.topic_clusters(db, lookback_hours=lookback_hours)


@router.get("/ticker/{ticker}/articles", response_model=TickerArticleTableResponse)
def ticker_article_table(
    ticker: str,
    lookback_hours: int = Query(default=72, ge=1, le=720),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0, le=10000),
    db: Session = Depends(get_db),
) -> TickerArticleTableResponse:
    return aggregation_service.ticker_article_table(
        db,
        ticker=ticker,
        lookback_hours=lookback_hours,
        limit=limit,
        offset=offset,
    )
