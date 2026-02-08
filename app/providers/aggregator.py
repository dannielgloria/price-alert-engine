import time
import random
from dataclasses import dataclass

from app.settings import settings
from app.providers.base import PricePoint
from app.providers.binance import BinanceProvider
from app.providers.coinbase import CoinbaseProvider
from app.providers.coingecko import CoinGeckoProvider

@dataclass
class Cached:
    ts: int
    pricepoint: PricePoint

class ProviderAggregator:
    def __init__(self):
        self.providers = {
            "BINANCE": BinanceProvider(),
            "COINBASE": CoinbaseProvider(),
            "COINGECKO": CoinGeckoProvider(),
        }
        self.order = [p.strip().upper() for p in settings.provider_order.split(",") if p.strip()]
        self.cache: dict[str, Cached] = {}

    def _cache_key(self, asset: dict) -> str:
        return asset.get("symbol", "UNK").upper()

    async def get_pricepoint(self, asset: dict) -> PricePoint:
        key = self._cache_key(asset)
        now = int(time.time())
        cached = self.cache.get(key)
        if cached and (now - cached.ts) <= settings.price_cache_ttl_sec:
            return cached.pricepoint

        # fallback with retry/backoff per provider
        last_err: Exception | None = None
        for pname in self.order:
            prov = self.providers.get(pname)
            if not prov:
                continue

            for attempt in range(3):
                try:
                    pp = await prov.get_pricepoint(asset)
                    self.cache[key] = Cached(ts=now, pricepoint=pp)
                    return pp
                except Exception as e:
                    last_err = e
                    backoff = (0.4 * (2 ** attempt)) + random.random() * 0.2
                    await _sleep(backoff)

        raise RuntimeError(f"all_providers_failed: {last_err}")

async def _sleep(sec: float) -> None:
    import asyncio
    await asyncio.sleep(sec)
