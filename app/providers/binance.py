import random
import time
import httpx
from app.settings import settings
from app.providers.base import PricePoint

class BinanceProvider:
    name = "BINANCE"
    base_url = "https://api.binance.com"

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

        symbol = asset.get("binance_symbol")
        if not symbol:
            raise RuntimeError("no_binance_symbol")

        timeout = httpx.Timeout(settings.http_timeout_sec)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # last price
            r = await client.get(f"{self.base_url}/api/v3/ticker/price", params={"symbol": symbol})
            r.raise_for_status()
            last = float(r.json()["price"])

            # klines: 1h candles, last 300 closes
            r2 = await client.get(
                f"{self.base_url}/api/v3/klines",
                params={"symbol": symbol, "interval": "1h", "limit": 300},
            )
            r2.raise_for_status()
            kl = r2.json()
            closes = [float(x[4]) for x in kl]  # close index 4

        self._cb_on_success()
        return PricePoint(last=last, ohlcv_close=closes)
