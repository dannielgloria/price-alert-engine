from sqlalchemy import String, Boolean, Float, Integer, DateTime, ForeignKey, UniqueConstraint, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.persistence.db import Base

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # mappings (treat symbols as data)
    binance_symbol: Mapped[str | None] = mapped_column(String(64), nullable=True)
    coinbase_product_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    coingecko_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    entry: Mapped[float] = mapped_column(Float)
    invested_amount: Mapped[float] = mapped_column(Float)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Strategy(Base):
    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    base_tp: Mapped[float] = mapped_column(Float, default=0.10)
    sl_pct: Mapped[float] = mapped_column(Float, default=0.08)
    trail_atr_mult: Mapped[float] = mapped_column(Float, default=2.5)
    profit_lock_pct: Mapped[float] = mapped_column(Float, default=0.06)
    cooldown_sec: Mapped[int] = mapped_column(Integer, default=1800)
    confirm_regime: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

class EngineState(Base):
    __tablename__ = "engine_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    holding_id: Mapped[int] = mapped_column(Integer, ForeignKey("holdings.id", ondelete="CASCADE"), unique=True)

    trailing_active: Mapped[bool] = mapped_column(Boolean, default=False)
    trailing_anchor: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_alert_ts: Mapped[int | None] = mapped_column(Integer, nullable=True)

    holding = relationship("Holding")

class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        UniqueConstraint("holding_id", "kind", "bucket", name="uq_alert_dedup"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    holding_id: Mapped[int] = mapped_column(Integer, ForeignKey("holdings.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    bucket: Mapped[int] = mapped_column(Integer, index=True)  # timestamp bucket for idempotency
    message: Mapped[str] = mapped_column(Text)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    holding = relationship("Holding")
