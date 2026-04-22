from datetime import datetime, timezone
import random

from app.schemas.replay import ReplayEvent, ReplayRequest, ReplayResponse


class ReplayService:
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def generate(self, payload: ReplayRequest) -> ReplayResponse:
        rng = random.Random(payload.seed)
        events: list[ReplayEvent] = []
        for step in range(1, payload.steps + 1):
            for ticker in [ticker.upper() for ticker in payload.tickers]:
                raw = rng.uniform(-1.0, 1.0)
                signal = "BUY" if raw > 0.25 else "SELL" if raw < -0.25 else "HOLD"
                label = "positive" if raw > 0.1 else "negative" if raw < -0.1 else "neutral"
                events.append(
                    ReplayEvent(
                        ticker=ticker,
                        step=step,
                        label=label,
                        score=round(abs(raw), 4),
                        confidence=round(0.45 + min(abs(raw), 0.5), 4),
                        signal=signal,
                    )
                )
        return ReplayResponse(generated_at=self._utc_now(), events=events)


replay_service = ReplayService()
