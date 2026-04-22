from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import uuid

from fastapi import HTTPException, Request

from app.core.config import settings


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RequestRateLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        self.limit_per_minute = max(limit_per_minute, 10)
        self._windows: dict[str, deque[datetime]] = defaultdict(deque)

    def check(self, client_key: str) -> None:
        current = now_utc()
        cutoff = current - timedelta(minutes=1)
        window = self._windows[client_key]
        while window and window[0] < cutoff:
            window.popleft()
        if len(window) >= self.limit_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        window.append(current)


rate_limiter = RequestRateLimiter(settings.API_RATE_LIMIT_PER_MINUTE)


async def inject_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


def enforce_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    rate_limiter.check(client_host)
