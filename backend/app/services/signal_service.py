from datetime import datetime

from app.schemas.analytics import TickerAggregationResponse
from app.schemas.sentiment import SignalResponse


class SignalService:
    def generate_from_aggregate(self, aggregate: TickerAggregationResponse) -> SignalResponse:
        if aggregate.article_count == 0:
            return SignalResponse(
                ticker=aggregate.ticker,
                signal="HOLD",
                confidence=0.0,
                rationale="No recent sentiment coverage",
                generated_at=datetime.utcnow(),
            )

        if aggregate.avg_score >= 0.72 and aggregate.positive_ratio >= 0.55:
            signal = "BUY"
            rationale = "Positive sentiment breadth with strong average confidence"
        elif aggregate.avg_score <= 0.45 and aggregate.negative_ratio >= 0.5:
            signal = "SELL"
            rationale = "Negative sentiment dominance and weak average confidence"
        else:
            signal = "HOLD"
            rationale = "Mixed sentiment profile without strong directional edge"

        confidence = round(max(aggregate.positive_ratio, aggregate.negative_ratio), 4)
        return SignalResponse(
            ticker=aggregate.ticker,
            signal=signal,
            confidence=confidence,
            rationale=rationale,
            generated_at=datetime.utcnow(),
        )


signal_service = SignalService()
