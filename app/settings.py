from pydantic import BaseModel
import os

def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default

def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data.db")

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    poll_interval_sec: int = _get_int("POLL_INTERVAL_SEC", 30)
    http_timeout_sec: float = _get_float("HTTP_TIMEOUT_SEC", 8.0)

    ema_short: int = _get_int("EMA_SHORT", 50)
    ema_long: int = _get_int("EMA_LONG", 200)
    atr_period: int = _get_int("ATR_PERIOD", 14)
    vol_window: int = _get_int("VOL_WINDOW", 30)

    provider_order: str = os.getenv("PROVIDER_ORDER", "BINANCE,COINBASE,COINGECKO")

    cb_fail_threshold: int = _get_int("CB_FAIL_THRESHOLD", 4)
    cb_open_seconds: int = _get_int("CB_OPEN_SECONDS", 120)

    price_cache_ttl_sec: int = _get_int("PRICE_CACHE_TTL_SEC", 8)

settings = Settings()
