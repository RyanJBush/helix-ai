from datetime import datetime, timezone

from app.core.config import settings

SOURCE_WEIGHTS: dict[str, float] = {
    "financial_news": 1.0,
    "press_release": 0.85,
    "earnings_wire": 1.15,
    "social_curated": 0.55,
}


def get_source_weight(source: str) -> float:
    return SOURCE_WEIGHTS.get(source, 0.7)


def market_hours_multiplier(timestamp: datetime) -> float:
    # Approximate US market hours in UTC (13:30-20:00, weekdays).
    if timestamp.weekday() >= 5:
        return 0.9
    minutes = timestamp.hour * 60 + timestamp.minute
    if 13 * 60 + 30 <= minutes <= 20 * 60:
        return 1.1
    return 0.95


def time_decay_multiplier(created_at: datetime, now: datetime | None = None) -> float:
    now_utc = now or datetime.now(timezone.utc).replace(tzinfo=None)
    age_hours = max((now_utc - created_at).total_seconds() / 3600, 0.0)
    half_life = max(settings.SENTIMENT_HALF_LIFE_HOURS, 0.5)
    return 0.5 ** (age_hours / half_life)
