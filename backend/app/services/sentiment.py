from __future__ import annotations

from threading import Lock


class SentimentAnalyzer:
    def __init__(self) -> None:
        self._classifier = None
        self._init_lock = Lock()

    def _load_pipeline(self):
        try:
            from transformers import pipeline

            return pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert",
            )
        except Exception:
            return None

    def _ensure_pipeline(self):
        if self._classifier is not None:
            return self._classifier

        with self._init_lock:
            if self._classifier is None:
                self._classifier = self._load_pipeline()

        return self._classifier

    def analyze(self, text: str) -> tuple[float, str]:
        classifier = self._ensure_pipeline()
        if classifier:
            result = classifier(text[:512])[0]
            label = str(result["label"]).lower()
            confidence = float(result["score"])
            if "positive" in label:
                return confidence, "positive"
            if "negative" in label:
                return -confidence, "negative"
            return 0.0, "neutral"

        return self._keyword_fallback(text)

    @staticmethod
    def _keyword_fallback(text: str) -> tuple[float, str]:
        text_lower = text.lower()
        positive_hits = sum(
            token in text_lower
            for token in ("beat", "growth", "rally", "surge", "upgrade", "strong")
        )
        negative_hits = sum(
            token in text_lower
            for token in ("miss", "drop", "fall", "downgrade", "weak", "risk")
        )

        score = (positive_hits - negative_hits) / 5
        if score > 0.2:
            return min(score, 1.0), "positive"
        if score < -0.2:
            return max(score, -1.0), "negative"
        return score, "neutral"
