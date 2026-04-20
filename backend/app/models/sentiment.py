from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SentimentRecord(Base):
    __tablename__ = "sentiment_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(12), index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    news_item_id: Mapped[int | None] = mapped_column(ForeignKey("news_items.id"), nullable=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    source_weight: Mapped[float] = mapped_column(Float, default=1.0)
    model_used: Mapped[str] = mapped_column(String(64), default="finbert_fallback")
    label: Mapped[str] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
