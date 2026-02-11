from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.persistence.db import SessionLocal
from app.persistence.repo import Repo
from app.domain.schemas import HoldingIn, HoldingOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[HoldingOut])
def list_holdings(symbol: str | None = None, db: Session = Depends(get_db)):
    repo = Repo(db)
    hs = repo.list_holdings(symbol)
    return [HoldingOut(id=h.id, symbol=h.symbol, entry=h.entry, invested_amount=h.invested_amount) for h in hs]

@router.post("", response_model=HoldingOut)
def create_holding(body: HoldingIn, db: Session = Depends(get_db)):
    repo = Repo(db)
    h = repo.create_holding(body.model_dump())
    return HoldingOut(id=h.id, symbol=h.symbol, entry=h.entry, invested_amount=h.invested_amount)
