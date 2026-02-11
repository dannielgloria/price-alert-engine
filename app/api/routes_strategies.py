from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.persistence.db import SessionLocal
from app.persistence.repo import Repo
from app.domain.schemas import StrategyIn, StrategyOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{symbol}", response_model=StrategyOut)
def get_strategy(symbol: str, db: Session = Depends(get_db)):
    repo = Repo(db)
    s = repo.get_or_create_strategy(symbol)
    return StrategyOut(
        id=s.id,
        symbol=s.symbol,
        base_tp=s.base_tp,
        sl_pct=s.sl_pct,
        trail_atr_mult=s.trail_atr_mult,
        profit_lock_pct=s.profit_lock_pct,
        cooldown_sec=s.cooldown_sec,
        confirm_regime=s.confirm_regime,
    )

@router.put("/{symbol}", response_model=StrategyOut)
def upsert_strategy(symbol: str, body: StrategyIn, db: Session = Depends(get_db)):
    repo = Repo(db)
    s = repo.upsert_strategy(symbol, body.model_dump())
    return StrategyOut(
        id=s.id,
        symbol=s.symbol,
        base_tp=s.base_tp,
        sl_pct=s.sl_pct,
        trail_atr_mult=s.trail_atr_mult,
        profit_lock_pct=s.profit_lock_pct,
        cooldown_sec=s.cooldown_sec,
        confirm_regime=s.confirm_regime,
    )
