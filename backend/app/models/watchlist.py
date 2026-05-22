from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    owner: Mapped[str] = mapped_column(String(64), default="demo_user", index=True)
    tickers_csv: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class MarketCapSnapshot(Base):
    __tablename__ = "market_cap_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(12), index=True)
    market_cap: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(64), default="atlas_mock")
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
