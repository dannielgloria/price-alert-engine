from pydantic import BaseModel, Field

class AssetIn(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=32)
    enabled: bool = True
    binance_symbol: str | None = None
    coinbase_product_id: str | None = None
    coingecko_id: str | None = None

class AssetOut(AssetIn):
    id: int

class HoldingIn(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=32)
    entry: float = Field(..., gt=0)
    invested_amount: float = Field(..., gt=0)

class HoldingOut(HoldingIn):
    id: int

class StrategyIn(BaseModel):
    base_tp: float = Field(0.10, ge=0, le=10)
    sl_pct: float = Field(0.08, ge=0, le=1)
    trail_atr_mult: float = Field(2.5, ge=0.1, le=100)
    profit_lock_pct: float = Field(0.06, ge=0, le=10)
    cooldown_sec: int = Field(1800, ge=0, le=7 * 24 * 3600)
    confirm_regime: bool = True

class StrategyOut(StrategyIn):
    id: int
    symbol: str
