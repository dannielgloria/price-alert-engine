import time
import httpx
from app.settings import settings
from app.providers.base import PricePoint

class CoinbaseProvider:
    name = "COINBASE"
    base_url = "https://api.exchange.coinbase.com"

    def __init__(self):
        self._fail_count = 0
        self._cb_open_until = 0

    def _cb_allow(self) -> bool:
        return int(time.time()) >= self._cb_open_until

    def _cb_on_failure(self) -> None:
        self._fail_count += 1
        if self._fail_count >= settings.cb_fail_threshold:
            self._cb_open_until = int(time.time()) + settings.cb_open_seconds

    def _cb_on_success(self) -> None:
        self._fail_count = 0
        self._cb_open_until = 0

    async def get_pricepoint(self, asset: dict) -> PricePoint:
        if not self._cb_allow():
            raise RuntimeError("circuit_open")

        product_id = asset.get("coinbase_product_id")
        if not product_id:
            raise RuntimeError("no_coinbase_product_id")

        timeout = httpx.Timeout(settings.http_timeout_sec)
        headers = {"User-Agent": "price-alert-engine/1.0"}
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            # ticker (last)
            r = await client.get(f"{self.base_url}/products/{product_id}/ticker")
            r.raise_for_status()
            last = float(r.json()["price"])

            # candles (1h, 300 points) - Coinbase returns [time, low, high, open, close, volume]
            r2 = await client.get(
                f"{self.base_url}/products/{product_id}/candles",
                params={"granularity": 3600},
            )
            r2.raise_for_status()
            candles = r2.json()
            # returned in reverse chronological order
            candles_sorted = sorted(candles, key=lambda x: x[0])[-300:]
            closes = [float(x[4]) for x in candles_sorted]

        self._cb_on_success()
        return PricePoint(last=last, ohlcv_close=closes)
