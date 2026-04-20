from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.config import settings
from app.schemas.analytics import TickerAggregationResponse
from app.schemas.sentiment import SignalResponse


@dataclass
class SignalThresholds:
    buy_threshold: float = settings.DEFAULT_BUY_THRESHOLD
    sell_threshold: float = settings.DEFAULT_SELL_THRESHOLD
    min_confidence: float = settings.DEFAULT_MIN_SIGNAL_CONFIDENCE


class SignalService:
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _clamp_confidence(value: float) -> float:
        return round(max(0.0, min(value, 1.0)), 4)

    def generate_from_aggregate(
        self,
        aggregate: TickerAggregationResponse,
        thresholds: SignalThresholds | None = None,
    ) -> SignalResponse:
        config = thresholds or SignalThresholds()

        if aggregate.article_count == 0:
            return SignalResponse(
                ticker=aggregate.ticker,
                signal="HOLD",
                confidence=0.0,
                weighted_score=aggregate.weighted_sentiment_score,
                buy_threshold=config.buy_threshold,
                sell_threshold=config.sell_threshold,
                min_confidence=config.min_confidence,
                rationale="No recent sentiment coverage",
                generated_at=self._utc_now(),
            )

        if aggregate.weighted_confidence < config.min_confidence:
            return SignalResponse(
                ticker=aggregate.ticker,
                signal="HOLD",
                confidence=self._clamp_confidence(aggregate.weighted_confidence),
                weighted_score=aggregate.weighted_sentiment_score,
                buy_threshold=config.buy_threshold,
                sell_threshold=config.sell_threshold,
                min_confidence=config.min_confidence,
                rationale="Weighted confidence below minimum threshold",
                generated_at=self._utc_now(),
            )

        if aggregate.weighted_sentiment_score >= config.buy_threshold:
            signal = "BUY"
            rationale = "Weighted sentiment exceeded buy threshold"
        elif aggregate.weighted_sentiment_score <= config.sell_threshold:
            signal = "SELL"
            rationale = "Weighted sentiment fell below sell threshold"
        else:
            signal = "HOLD"
            rationale = "Weighted sentiment remained within hold band"

        confidence = self._clamp_confidence((abs(aggregate.weighted_sentiment_score) * 0.6) + (aggregate.weighted_confidence * 0.4))
        return SignalResponse(
            ticker=aggregate.ticker,
            signal=signal,
            confidence=confidence,
            weighted_score=round(aggregate.weighted_sentiment_score, 4),
            buy_threshold=config.buy_threshold,
            sell_threshold=config.sell_threshold,
            min_confidence=config.min_confidence,
            rationale=rationale,
            generated_at=self._utc_now(),
        )


signal_service = SignalService()
