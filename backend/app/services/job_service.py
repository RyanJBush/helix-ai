from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from app.schemas.jobs import JobResponse
from app.schemas.news import IngestNewsRequest
from app.schemas.sentiment import SentimentRequest
from app.services.news_service import news_ingestion_service
from app.services.nlp_service import nlp_service
from app.services.stream_service import stream_manager
from app.services.weighting_service import get_source_weight
from app.models.sentiment import SentimentRecord


@dataclass
class JobState:
    job_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    records_processed: int = 0
    error_message: str | None = None


class JobService:
    def __init__(self) -> None:
        self._jobs: dict[str, JobState] = {}

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def _to_response(self, job_id: str, state: JobState) -> JobResponse:
        return JobResponse(
            job_id=job_id,
            job_type=state.job_type,  # type: ignore[arg-type]
            status=state.status,  # type: ignore[arg-type]
            created_at=state.created_at,
            updated_at=state.updated_at,
            records_processed=state.records_processed,
            error_message=state.error_message,
        )

    def create_job(self, job_type: str) -> str:
        job_id = str(uuid.uuid4())
        now = self._utc_now()
        self._jobs[job_id] = JobState(job_type=job_type, status="queued", created_at=now, updated_at=now)
        return job_id

    def set_running(self, job_id: str) -> None:
        if job_id in self._jobs:
            self._jobs[job_id].status = "running"
            self._jobs[job_id].updated_at = self._utc_now()

    def set_completed(self, job_id: str, processed: int) -> None:
        if job_id in self._jobs:
            self._jobs[job_id].status = "completed"
            self._jobs[job_id].records_processed = processed
            self._jobs[job_id].updated_at = self._utc_now()

    def set_failed(self, job_id: str, error: str) -> None:
        if job_id in self._jobs:
            self._jobs[job_id].status = "failed"
            self._jobs[job_id].error_message = error
            self._jobs[job_id].updated_at = self._utc_now()

    def get_job(self, job_id: str) -> JobResponse | None:
        state = self._jobs.get(job_id)
        if state is None:
            return None
        return self._to_response(job_id, state)

    async def run_ingestion_job(self, job_id: str, payload: IngestNewsRequest, db) -> None:
        self.set_running(job_id)
        await stream_manager.broadcast({"event": "job_update", "job_id": job_id, "status": "running"})
        try:
            result = news_ingestion_service.ingest_news(db, payload)
            self.set_completed(job_id, processed=len(result.items))
            await stream_manager.broadcast(
                {"event": "job_update", "job_id": job_id, "status": "completed", "processed": len(result.items)}
            )
        except Exception as exc:  # noqa: BLE001
            self.set_failed(job_id, str(exc))
            await stream_manager.broadcast({"event": "job_update", "job_id": job_id, "status": "failed", "error": str(exc)})

    async def run_sentiment_batch_job(self, job_id: str, items: list[SentimentRequest], db) -> None:
        self.set_running(job_id)
        await stream_manager.broadcast({"event": "job_update", "job_id": job_id, "status": "running"})
        processed = 0
        try:
            for payload in items:
                result = nlp_service.analyze_sentiment(payload)
                text = (payload.text or " ".join(part for part in [payload.headline, payload.body] if part)).strip()
                db.add(
                    SentimentRecord(
                        ticker=result.ticker,
                        source=payload.source,
                        news_item_id=payload.news_item_id,
                        text=text,
                        score=result.score,
                        confidence=result.confidence,
                        source_weight=get_source_weight(payload.source),
                        model_used=result.model_used,
                        label=result.label,
                    )
                )
                processed += 1
            db.commit()
            self.set_completed(job_id, processed=processed)
            await stream_manager.broadcast(
                {"event": "job_update", "job_id": job_id, "status": "completed", "processed": processed}
            )
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            self.set_failed(job_id, str(exc))
            await stream_manager.broadcast({"event": "job_update", "job_id": job_id, "status": "failed", "error": str(exc)})


job_service = JobService()
