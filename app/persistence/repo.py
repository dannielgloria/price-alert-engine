import time
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.models import Asset, Holding, Strategy, EngineState, Alert
from app.domain.signals import SignalKind

class Repo:
    def __init__(self, db: Session):
        self.db = db

    # -------- Assets --------
    def list_enabled_assets(self) -> list[Asset]:
        q = select(Asset).where(Asset.enabled == True)  # noqa: E712
        return list(self.db.execute(q).scalars().all())

    def upsert_asset(self, data: dict) -> Asset:
        symbol = data["symbol"].upper().strip()
        q = select(Asset).where(Asset.symbol == symbol)
        existing = self.db.execute(q).scalars().first()
        if existing:
            for k, v in data.items():
                if k == "symbol":
                    continue
                setattr(existing, k, v)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        asset = Asset(symbol=symbol, **{k: v for k, v in data.items() if k != "symbol"})
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    # -------- Holdings --------
    def create_holding(self, data: dict) -> Holding:
        h = Holding(
            symbol=data["symbol"].upper().strip(),
            entry=data["entry"],
            invested_amount=data["invested_amount"],
        )
        self.db.add(h)
        self.db.commit()
        self.db.refresh(h)

        # ensure state exists
        st = EngineState(holding_id=h.id, trailing_active=False, trailing_anchor=None, last_alert_ts=None)
        self.db.add(st)
        self.db.commit()
        return h

    def list_holdings(self, symbol: str | None = None) -> list[Holding]:
        q = select(Holding)
        if symbol:
            q = q.where(Holding.symbol == symbol.upper().strip())
        return list(self.db.execute(q).scalars().all())

    # -------- Strategies --------
    def get_or_create_strategy(self, symbol: str) -> Strategy:
        sym = symbol.upper().strip()
        q = select(Strategy).where(Strategy.symbol == sym)
        s = self.db.execute(q).scalars().first()
        if s:
            return s
        s = Strategy(symbol=sym)
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return s

    def upsert_strategy(self, symbol: str, data: dict) -> Strategy:
        s = self.get_or_create_strategy(symbol)
        for k, v in data.items():
            setattr(s, k, v)
        self.db.commit()
        self.db.refresh(s)
        return s

    # -------- Engine State --------
    def load_state(self, holding_id: int) -> EngineState:
        q = select(EngineState).where(EngineState.holding_id == holding_id)
        st = self.db.execute(q).scalars().first()
        if not st:
            st = EngineState(holding_id=holding_id, trailing_active=False, trailing_anchor=None, last_alert_ts=None)
            self.db.add(st)
            self.db.commit()
            self.db.refresh(st)
        return st

    def save_state(self, st: EngineState) -> None:
        self.db.add(st)
        self.db.commit()

    # -------- Alerts / Dedup --------
    @staticmethod
    def _bucket(now_ts: int, seconds: int = 300) -> int:
        return now_ts - (now_ts % seconds)

    def should_send_alert(self, holding_id: int, kind: SignalKind, now_ts: int, bucket_seconds: int = 300) -> bool:
        bucket = self._bucket(now_ts, bucket_seconds)
        q = select(Alert).where(
            Alert.holding_id == holding_id,
            Alert.kind == str(kind),
            Alert.bucket == bucket,
        )
        exists = self.db.execute(q).scalars().first()
        return exists is None

    def record_alert(self, holding_id: int, kind: SignalKind, message: str, now_ts: int, bucket_seconds: int = 300) -> None:
        bucket = self._bucket(now_ts, bucket_seconds)
        a = Alert(holding_id=holding_id, kind=str(kind), bucket=bucket, message=message)
        self.db.add(a)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
