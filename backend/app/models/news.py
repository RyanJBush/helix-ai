from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(12), index=True)
    source: Mapped[str] = mapped_column(String(64), default="mock")
    source_type: Mapped[str] = mapped_column(String(64), default="financial_news", index=True)
    source_weight: Mapped[float] = mapped_column(Float, default=1.0)
    event_type: Mapped[str] = mapped_column(String(64), default="general_news", index=True)
    market_session: Mapped[str] = mapped_column(String(24), default="closed", index=True)
    related_tickers: Mapped[str] = mapped_column(Text, default="")
    dedupe_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    headline: Mapped[str] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
