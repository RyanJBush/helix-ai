from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.analytics import TickerAggregationResponse
from app.schemas.sentiment import SignalResponse


@dataclass
class SignalThresholds:
    buy_threshold: float = settings.DEFAULT_BUY_THRESHOLD
    sell_threshold: float = settings.DEFAULT_SELL_THRESHOLD
    min_confidence: float = settings.DEFAULT_MIN_SIGNAL_CONFIDENCE


@dataclass
class SignalContext:
    event_impact: float = 0.0
    volume_zscore: float = 0.0
    price_momentum: float = 0.0
    watchlist_priority: float = 0.0


@dataclass
class SignalRuntimeConfig:
    cooldown_minutes: int = 30
    sharp_shift_delta: float = 0.45
    factors: dict[str, float] = field(default_factory=dict)


class SignalService:
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _clamp_confidence(value: float) -> float:
        return round(max(0.0, min(value, 1.0)), 4)

    def generate_from_aggregate(
        self,
        aggregate: TickerAggregationResponse,
        thresholds: SignalThresholds | None = None,
        context: SignalContext | None = None,
        recent_signals: list[str] | None = None,
        runtime: SignalRuntimeConfig | None = None,
    ) -> SignalResponse:
        config = thresholds or SignalThresholds()
        signal_context = context or SignalContext()
        runtime_config = runtime or SignalRuntimeConfig()
        buy_threshold = max(config.buy_threshold, 0.0)
        sell_threshold = min(config.sell_threshold, 0.0)
        min_confidence = self._clamp_confidence(config.min_confidence)
        context_shift = (
            (signal_context.event_impact * 0.35)
            + (signal_context.volume_zscore * 0.10)
            + (signal_context.price_momentum * 0.25)
            + (signal_context.watchlist_priority * 0.15)
        )
        adjusted_score = aggregate.weighted_sentiment_score + context_shift

        if aggregate.article_count == 0:
            return SignalResponse(
                ticker=aggregate.ticker,
                signal="HOLD",
                confidence=0.0,
                weighted_score=aggregate.weighted_sentiment_score,
                buy_threshold=buy_threshold,
                sell_threshold=sell_threshold,
                min_confidence=min_confidence,
                signal_strength=0.0,
                factors={"context_shift": round(context_shift, 4)},
                rationale="No recent sentiment coverage",
                generated_at=self._utc_now(),
            )

        if aggregate.weighted_confidence < min_confidence:
            return SignalResponse(
                ticker=aggregate.ticker,
                signal="HOLD",
                confidence=self._clamp_confidence(aggregate.weighted_confidence),
                weighted_score=aggregate.weighted_sentiment_score,
                buy_threshold=buy_threshold,
                sell_threshold=sell_threshold,
                min_confidence=min_confidence,
                signal_strength=0.0,
                factors={"context_shift": round(context_shift, 4)},
                rationale="Weighted confidence below minimum threshold",
                generated_at=self._utc_now(),
            )

        if adjusted_score >= buy_threshold:
            signal = "BUY"
            threshold_gap = adjusted_score - buy_threshold
            rationale = f"Weighted sentiment exceeded buy threshold by {threshold_gap:.3f}"
        elif adjusted_score <= sell_threshold:
            signal = "SELL"
            threshold_gap = sell_threshold - adjusted_score
            rationale = f"Weighted sentiment fell below sell threshold by {threshold_gap:.3f}"
        else:
            signal = "HOLD"
            rationale = "Weighted sentiment remained within hold band"

        if recent_signals and signal != "HOLD":
            latest = recent_signals[0]
            opposite = (latest == "BUY" and signal == "SELL") or (latest == "SELL" and signal == "BUY")
            if opposite:
                signal = "HOLD"
                rationale = f"Conflicting prior signal in cooldown window ({runtime_config.cooldown_minutes}m)"

        confidence = self._clamp_confidence(
            (abs(adjusted_score) * 0.55)
            + (aggregate.weighted_confidence * 0.35)
            + (min(aggregate.article_count, 10) / 10.0 * 0.10)
        )
        alert = None
        if abs(adjusted_score - aggregate.weighted_sentiment_score) >= runtime_config.sharp_shift_delta:
            alert = "sharp_shift"

        signal_strength = self._clamp_confidence(abs(adjusted_score))
        factors = {
            "weighted_sentiment_score": round(aggregate.weighted_sentiment_score, 4),
            "context_shift": round(context_shift, 4),
            "event_impact": round(signal_context.event_impact, 4),
            "volume_zscore": round(signal_context.volume_zscore, 4),
            "price_momentum": round(signal_context.price_momentum, 4),
            "watchlist_priority": round(signal_context.watchlist_priority, 4),
        }
        return SignalResponse(
            ticker=aggregate.ticker,
            signal=signal,
            confidence=confidence,
            weighted_score=round(adjusted_score, 4),
            buy_threshold=buy_threshold,
            sell_threshold=sell_threshold,
            min_confidence=min_confidence,
            signal_strength=signal_strength,
            factors=factors,
            alert=alert,
            rationale=rationale,
            generated_at=self._utc_now(),
        )


signal_service = SignalService()
