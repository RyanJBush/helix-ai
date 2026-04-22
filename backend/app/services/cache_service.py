from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: datetime


class TtlCache(Generic[T]):
    def __init__(self, ttl_seconds: int = 30) -> None:
        self.ttl_seconds = max(ttl_seconds, 1)
        self._store: dict[str, CacheEntry[T]] = {}

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def get(self, key: str) -> T | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at < self._now():
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: T) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=self._now() + timedelta(seconds=self.ttl_seconds))

    def clear(self) -> None:
        self._store.clear()
