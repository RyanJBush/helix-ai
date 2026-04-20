import logging
from datetime import UTC, datetime

from transformers import pipeline

from app.core.config import settings
from app.schemas.sentiment import SentimentRequest, SentimentResponse

logger = logging.getLogger(__name__)

FIN_POSITIVE_TERMS = {"beat", "outperform", "upgrade", "guidance raise", "margin expansion", "record revenue"}
FIN_NEGATIVE_TERMS = {"miss", "downgrade", "guidance cut", "impairment", "liquidity stress", "margin compression"}
FIN_UNCERTAINTY_TERMS = {"uncertain", "volatile", "headwind", "challenging", "risk", "caution"}


class NLPService:
    def __init__(self) -> None:
        self._classifier = None

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def _load_classifier(self):
        if self._classifier is None:
            logger.info("Loading NLP model: %s", settings.NLP_MODEL_NAME)
            self._classifier = pipeline("sentiment-analysis", model=settings.NLP_MODEL_NAME)

    @staticmethod
    def _fallback_score(text: str) -> tuple[str, float]:
        lower = text.lower()
        pos_hits = sum(1 for term in FIN_POSITIVE_TERMS if term in lower)
        neg_hits = sum(1 for term in FIN_NEGATIVE_TERMS if term in lower)

        if pos_hits > neg_hits:
            return "positive", min(0.55 + 0.08 * pos_hits, 0.95)
        if neg_hits > pos_hits:
            return "negative", min(0.55 + 0.08 * neg_hits, 0.95)
        return "neutral", 0.5

    @staticmethod
    def _normalize_label(label: str) -> str:
        lowered = label.lower()
        if "pos" in lowered:
            return "positive"
        if "neg" in lowered:
            return "negative"
        return "neutral"

    @staticmethod
    def _finance_confidence(text: str, label: str, score: float) -> float:
        lower = text.lower()
        pos_hits = sum(1 for term in FIN_POSITIVE_TERMS if term in lower)
        neg_hits = sum(1 for term in FIN_NEGATIVE_TERMS if term in lower)
        uncertainty_hits = sum(1 for term in FIN_UNCERTAINTY_TERMS if term in lower)

        directional_hits = pos_hits if label == "positive" else neg_hits if label == "negative" else abs(pos_hits - neg_hits)
        confidence = 0.5 + (0.25 * min(directional_hits, 3) / 3.0)
        confidence += 0.25 * max(score - 0.5, 0.0) * 2.0
        confidence -= 0.15 * min(uncertainty_hits, 3) / 3.0

        return round(max(0.0, min(confidence, 1.0)), 4)

    def analyze_sentiment(self, payload: SentimentRequest) -> SentimentResponse:
        model_used = settings.NLP_MODEL_NAME
        try:
            self._load_classifier()
            result = self._classifier(payload.text[:512])[0]
            label = self._normalize_label(str(result["label"]))
            score = float(result["score"])
        except Exception as exc:  # noqa: BLE001
            logger.warning("NLP model unavailable, using fallback heuristic: %s", exc)
            label, score = self._fallback_score(payload.text)
            model_used = "finbert_fallback"

        confidence = self._finance_confidence(payload.text, label=label, score=score)

        return SentimentResponse(
            ticker=payload.ticker.upper(),
            label=label,
            score=score,
            confidence=confidence,
            model_used=model_used,
            processed_at=self._utc_now(),
        )


nlp_service = NLPService()
