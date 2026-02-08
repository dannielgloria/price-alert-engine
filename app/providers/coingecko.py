import time
import httpx
from app.settings import settings
from app.providers.base import PricePoint

class CoinGeckoProvider:
    name = "COINGECKO"
    base_url = "https://api.coingecko.com/api/v3"

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

        cg_id = asset.get("coingecko_id")
        if not cg_id:
            raise RuntimeError("no_coingecko_id")

        timeout = httpx.Timeout(settings.http_timeout_sec)
        headers = {"accept": "application/json"}
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            r = await client.get(
                f"{self.base_url}/simple/price",
                params={"ids": cg_id, "vs_currencies": "usd"},
            )
            r.raise_for_status()
            last = float(r.json()[cg_id]["usd"])

            # market chart (hourly-ish): last 7d, then take last 300 points as "closes"
            r2 = await client.get(
                f"{self.base_url}/coins/{cg_id}/market_chart",
                params={"vs_currency": "usd", "days": "7"},
            )
            r2.raise_for_status()
            prices = r2.json().get("prices", [])
            closes = [float(p[1]) for p in prices][-300:]

        self._cb_on_success()
        return PricePoint(last=last, ohlcv_close=closes)
