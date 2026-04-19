import logging
from datetime import datetime

from transformers import pipeline

from app.core.config import settings
from app.schemas.sentiment import SentimentRequest, SentimentResponse

logger = logging.getLogger(__name__)


class NLPService:
    def __init__(self) -> None:
        self._classifier = None

    def _load_classifier(self):
        if self._classifier is None:
            logger.info("Loading NLP model: %s", settings.NLP_MODEL_NAME)
            self._classifier = pipeline("sentiment-analysis", model=settings.NLP_MODEL_NAME)

    @staticmethod
    def _fallback_score(text: str) -> tuple[str, float]:
        positive_terms = ["beat", "growth", "upgrade", "record", "strong"]
        negative_terms = ["miss", "downgrade", "weak", "lawsuit", "decline"]

        lower = text.lower()
        pos_hits = sum(1 for term in positive_terms if term in lower)
        neg_hits = sum(1 for term in negative_terms if term in lower)

        if pos_hits > neg_hits:
            return "positive", min(0.55 + 0.1 * pos_hits, 0.95)
        if neg_hits > pos_hits:
            return "negative", min(0.55 + 0.1 * neg_hits, 0.95)
        return "neutral", 0.5

    def analyze_sentiment(self, payload: SentimentRequest) -> SentimentResponse:
        try:
            self._load_classifier()
            result = self._classifier(payload.text[:512])[0]
            label = str(result["label"]).lower()
            score = float(result["score"])
        except Exception as exc:  # noqa: BLE001
            logger.warning("NLP model unavailable, using fallback heuristic: %s", exc)
            label, score = self._fallback_score(payload.text)

        return SentimentResponse(
            ticker=payload.ticker.upper(),
            label=label,
            score=score,
            processed_at=datetime.utcnow(),
        )


nlp_service = NLPService()
