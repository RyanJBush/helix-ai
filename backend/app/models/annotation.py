from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AnalystAnnotation(Base):
    __tablename__ = "analyst_annotations"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(12), index=True)
    signal_record_id: Mapped[int | None] = mapped_column(ForeignKey("signal_records.id"), nullable=True, index=True)
    author: Mapped[str] = mapped_column(String(64), default="system")
    note: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
