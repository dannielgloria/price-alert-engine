from dataclasses import dataclass
from typing import Protocol

@dataclass
class PricePoint:
    last: float
    ohlcv_close: list[float]  # closes for feature calcs

class PriceProvider(Protocol):
    name: str
    async def get_pricepoint(self, asset: dict) -> PricePoint: ...
