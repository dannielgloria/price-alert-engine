from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.persistence.db import SessionLocal
from app.persistence.repo import Repo
from app.domain.schemas import AssetIn, AssetOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[AssetOut])
def list_assets(db: Session = Depends(get_db)):
    repo = Repo(db)
    # list all (enabled + disabled)
    from sqlalchemy import select
    from app.domain.models import Asset
    rows = db.execute(select(Asset)).scalars().all()
    return [
        AssetOut(
            id=a.id,
            symbol=a.symbol,
            enabled=a.enabled,
            binance_symbol=a.binance_symbol,
            coinbase_product_id=a.coinbase_product_id,
            coingecko_id=a.coingecko_id,
        )
        for a in rows
    ]

@router.post("", response_model=AssetOut)
def upsert_asset(body: AssetIn, db: Session = Depends(get_db)):
    repo = Repo(db)
    a = repo.upsert_asset(body.model_dump())
    return AssetOut(
        id=a.id,
        symbol=a.symbol,
        enabled=a.enabled,
        binance_symbol=a.binance_symbol,
        coinbase_product_id=a.coinbase_product_id,
        coingecko_id=a.coingecko_id,
    )
