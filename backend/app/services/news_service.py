from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha1
import re

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.ingestion import IngestionRun
from app.models.news import NewsItem
from app.schemas.news import IngestNewsRequest, IngestionRunResponse, NewsItemResponse
from app.services.weighting_service import get_source_weight

SOURCE_DESCRIPTORS: dict[str, dict[str, str]] = {
    "financial_news": {"source": "marketwire", "event_type": "macro_news"},
    "press_release": {"source": "company_pr", "event_type": "corporate_update"},
    "earnings_wire": {"source": "earnings_desk", "event_type": "earnings"},
    "social_curated": {"source": "social_digest", "event_type": "social_sentiment"},
}

SOURCE_HEADLINES: dict[str, list[str]] = {
    "financial_news": [
        "{ticker} attracts fresh analyst attention after sector rotation",
        "{ticker} trading volume rises as institutions adjust positioning",
        "{ticker} sentiment improves following broad market rebound",
    ],
    "press_release": [
        "{ticker} announces strategic product and operations update",
        "{ticker} issues corporate guidance commentary for investors",
        "{ticker} shares quarterly business momentum highlights",
    ],
    "earnings_wire": [
        "{ticker} earnings commentary points to margin trajectory changes",
        "{ticker} revenue outlook revised in latest management remarks",
        "{ticker} posts quarterly print with mixed segment performance",
    ],
    "social_curated": [
        "Curated social feed shows retail sentiment shift around {ticker}",
        "{ticker} discussion volume spikes across curated investor channels",
        "Investor sentiment for {ticker} reflects mixed conviction signals",
    ],
}

UPPERCASE_TICKER_RE = re.compile(r"\b[A-Z]{1,5}\b")


@dataclass
class IngestionResult:
    run_id: int
    items: list[NewsItemResponse]


class NewsIngestionService:
    @staticmethod
    def _dedupe_key(ticker: str, source_type: str, headline: str) -> str:
        return sha1(f"{ticker}|{source_type}|{headline.strip().lower()}".encode("utf-8")).hexdigest()

    @staticmethod
    def _extract_related_tickers(text: str, ticker: str) -> list[str]:
        symbols = set(UPPERCASE_TICKER_RE.findall(text.upper()))
        symbols.add(ticker.upper())
        return sorted(symbols)

    @staticmethod
    def _market_session(published_at: datetime) -> str:
        if published_at.weekday() >= 5:
            return "weekend"
        minutes = published_at.hour * 60 + published_at.minute
        if 13 * 60 + 30 <= minutes <= 20 * 60:
            return "regular"
        if 11 * 60 <= minutes < 13 * 60 + 30:
            return "pre_market"
        if 20 * 60 < minutes <= 22 * 60:
            return "after_hours"
        return "closed"

    @staticmethod
    def _published_at_for(
        mode: str,
        ticker_idx: int,
        source_idx: int,
        article_idx: int,
        lookback_days: int,
    ) -> datetime:
        now = datetime.utcnow()
        if mode == "historical_backfill":
            offset_hours = (ticker_idx * 12) + (source_idx * 4) + (article_idx + 1) * 6
            return now - timedelta(hours=min(offset_hours, lookback_days * 24))
        return now - timedelta(minutes=(source_idx * 7) + (article_idx * 3))

    def ingest_news(self, db: Session, payload: IngestNewsRequest) -> IngestionResult:
        run = IngestionRun(
            status="running",
            mode=payload.mode,
            requested_tickers=",".join(sorted(t.upper() for t in payload.tickers)),
            requested_sources=",".join(payload.sources),
        )
        db.add(run)
        db.flush()

        inserted: list[NewsItemResponse] = []
        failures = 0

        try:
            for ticker_idx, raw_ticker in enumerate(payload.tickers):
                ticker = raw_ticker.upper()
                for source_idx, source_type in enumerate(payload.sources):
                    descriptor = SOURCE_DESCRIPTORS.get(source_type)
                    if descriptor is None:
                        failures += 1
                        continue

                    templates = SOURCE_HEADLINES.get(source_type, ["{ticker} trades flat as investors await catalyst"])
                    for article_idx, template in enumerate(templates[: payload.limit_per_ticker]):
                        published_at = self._published_at_for(
                            payload.mode,
                            ticker_idx=ticker_idx,
                            source_idx=source_idx,
                            article_idx=article_idx,
                            lookback_days=payload.lookback_days,
                        )
                        headline = template.format(ticker=ticker)
                        content = (
                            f"{headline}. Event classification: {descriptor['event_type']}."
                            f" Ingestion mode: {payload.mode}."
                        )
                        dedupe_key = self._dedupe_key(ticker=ticker, source_type=source_type, headline=headline)

                        existing = db.scalar(select(NewsItem.id).where(NewsItem.dedupe_key == dedupe_key))
                        if existing:
                            continue

                        related_tickers = self._extract_related_tickers(f"{headline} {content}", ticker=ticker)
                        item = NewsItem(
                            ticker=ticker,
                            source=descriptor["source"],
                            source_type=source_type,
                            source_weight=get_source_weight(source_type),
                            event_type=descriptor["event_type"],
                            market_session=self._market_session(published_at),
                            related_tickers=",".join(related_tickers),
                            dedupe_key=dedupe_key,
                            headline=headline,
                            content=content,
                            published_at=published_at,
                            ingested_at=datetime.utcnow(),
                        )
                        db.add(item)
                        db.flush()

                        inserted.append(
                            NewsItemResponse(
                                id=item.id,
                                ticker=item.ticker,
                                source=item.source,
                                source_type=item.source_type,
                                source_weight=item.source_weight,
                                event_type=item.event_type,
                                market_session=item.market_session,
                                related_tickers=related_tickers,
                                headline=item.headline,
                                content=item.content,
                                published_at=item.published_at,
                                ingested_at=item.ingested_at,
                            )
                        )

            run.records_inserted = len(inserted)
            run.failures_count = failures
            run.status = "completed" if failures == 0 else "partial_failed"
            run.completed_at = datetime.utcnow()
            db.add(run)
            db.commit()
            return IngestionResult(run_id=run.id, items=inserted)
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            run.status = "failed"
            run.error_message = str(exc)
            run.completed_at = datetime.utcnow()
            db.add(run)
            db.commit()
            return IngestionResult(run_id=run.id, items=[])

    def get_run_status(self, db: Session, run_id: int) -> IngestionRunResponse | None:
        run = db.get(IngestionRun, run_id)
        if run is None:
            return None
        return IngestionRunResponse(
            id=run.id,
            status=run.status,
            mode=run.mode,
            requested_tickers=run.requested_tickers.split(",") if run.requested_tickers else [],
            requested_sources=run.requested_sources.split(",") if run.requested_sources else [],
            records_inserted=run.records_inserted,
            failures_count=run.failures_count,
            error_message=run.error_message,
            started_at=run.started_at,
            completed_at=run.completed_at,
        )

    def latest_run_status(self, db: Session) -> IngestionRunResponse | None:
        latest = db.scalar(select(IngestionRun).order_by(desc(IngestionRun.started_at)).limit(1))
        if latest is None:
            return None
        return self.get_run_status(db, latest.id)


news_ingestion_service = NewsIngestionService()
