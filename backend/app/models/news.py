from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(12), index=True)
    source: Mapped[str] = mapped_column(String(64), default="mock")
    headline: Mapped[str] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
