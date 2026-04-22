import logging
from datetime import datetime, timezone
from hashlib import sha1
import re
from typing import Protocol

from transformers import pipeline

from app.core.config import settings
from app.schemas.sentiment import ModelComparison, SentimentRequest, SentimentResponse

logger = logging.getLogger(__name__)

FIN_POSITIVE_TERMS = {"beat", "outperform", "upgrade", "guidance raise", "margin expansion", "record revenue"}
FIN_NEGATIVE_TERMS = {"miss", "downgrade", "guidance cut", "impairment", "liquidity stress", "margin compression"}
FIN_UNCERTAINTY_TERMS = {"uncertain", "volatile", "headwind", "challenging", "risk", "caution"}
TOPIC_KEYWORDS: dict[str, set[str]] = {
    "earnings": {"earnings", "guidance", "quarter", "eps", "revenue"},
    "macro": {"rates", "inflation", "fed", "macro", "economy"},
    "product": {"launch", "product", "platform", "feature"},
    "legal": {"lawsuit", "regulatory", "fine", "settlement"},
    "m_and_a": {"acquire", "merger", "deal", "takeover"},
}
ENTITY_RE = re.compile(r"\b[A-Z]{1,5}\b")


class SentimentProvider(Protocol):
    def score(self, text: str) -> tuple[str, float]:
        ...


class TransformersSentimentProvider:
    def __init__(self) -> None:
        self._classifier = None

    def _load(self):
        if self._classifier is None:
            logger.info("Loading NLP model: %s", settings.NLP_MODEL_NAME)
            self._classifier = pipeline("sentiment-analysis", model=settings.NLP_MODEL_NAME)

    def score(self, text: str) -> tuple[str, float]:
        self._load()
        result = self._classifier(text[:512])[0]
        label = str(result["label"]).lower()
        if "pos" in label:
            normalized = "positive"
        elif "neg" in label:
            normalized = "negative"
        else:
            normalized = "neutral"
        return normalized, float(result["score"])


class NLPService:
    def __init__(self) -> None:
        self._provider: SentimentProvider = TransformersSentimentProvider()

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

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

    @staticmethod
    def _compose_text(payload: SentimentRequest) -> tuple[str, str, str]:
        headline = (payload.headline or "").strip()
        body = (payload.body or "").strip()
        text = (payload.text or "").strip()
        if not text:
            text = " ".join(part for part in [headline, body] if part).strip()
        if not headline:
            headline = text[:160]
        if not body:
            body = text
        return text, headline, body

    @staticmethod
    def _extract_topics_and_events(text: str) -> tuple[list[str], list[str]]:
        lower = text.lower()
        topics = [topic for topic, terms in TOPIC_KEYWORDS.items() if any(term in lower for term in terms)]
        if not topics:
            topics = ["general"]
        event_map = {
            "earnings": "earnings_update",
            "macro": "macro_event",
            "product": "product_update",
            "legal": "regulatory_event",
            "m_and_a": "corporate_action",
            "general": "general_news",
        }
        events = sorted({event_map.get(topic, "general_news") for topic in topics})
        return sorted(topics), events

    def _entity_sentiment(self, payload: SentimentRequest, text: str) -> dict[str, float]:
        entities = set(ENTITY_RE.findall(text.upper()))
        entities.add(payload.ticker.upper())
        base_label, base_score = self._fallback_score(text)
        direction = 1.0 if base_label == "positive" else -1.0 if base_label == "negative" else 0.0
        return {entity: round(direction * base_score, 4) for entity in sorted(entities)[:12]}

    def analyze_sentiment(self, payload: SentimentRequest) -> SentimentResponse:
        text, headline, body = self._compose_text(payload)
        model_used = settings.NLP_MODEL_NAME
        try:
            label, score = self._provider.score(text)
            label = self._normalize_label(label)
        except Exception as exc:  # noqa: BLE001
            logger.warning("NLP model unavailable, using fallback heuristic: %s", exc)
            label, score = self._fallback_score(text)
            model_used = "finbert_fallback"

        headline_label, headline_score = self._fallback_score(headline)
        body_label, body_score = self._fallback_score(body)
        confidence = self._finance_confidence(text, label=label, score=score)
        topics, events = self._extract_topics_and_events(text)
        cluster_id = sha1("|".join(topics).encode("utf-8")).hexdigest()[:12]

        model_comparison = None
        if payload.compare_models:
            baseline_label, baseline_score = self._fallback_score(text)
            model_comparison = ModelComparison(
                baseline_label=baseline_label,
                baseline_score=round(baseline_score, 4),
                advanced_label=label,
                advanced_score=round(score, 4),
                absolute_score_delta=round(abs(score - baseline_score), 4),
            )

        return SentimentResponse(
            ticker=payload.ticker.upper(),
            label=label,
            score=round(score, 4),
            headline_score=round(headline_score if headline_label == "positive" else -headline_score if headline_label == "negative" else 0.0, 4),
            body_score=round(body_score if body_label == "positive" else -body_score if body_label == "negative" else 0.0, 4),
            confidence=confidence,
            entity_sentiment=self._entity_sentiment(payload, text),
            topics=topics,
            events=events,
            cluster_id=cluster_id,
            model_used=model_used,
            model_comparison=model_comparison,
            processed_at=self._utc_now(),
        )


nlp_service = NLPService()
