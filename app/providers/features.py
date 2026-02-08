from dataclasses import dataclass
from math import sqrt
from app.settings import settings

@dataclass
class Features:
    last: float
    atr: float
    ema_short: float
    ema_long: float
    vol_pct: float
    regime: str  # BULL/BEAR/SIDEWAYS

def _ema(values: list[float], period: int) -> float:
    if not values:
        return 0.0
    k = 2 / (period + 1)
    ema = values[0]
    for v in values[1:]:
        ema = v * k + ema * (1 - k)
    return float(ema)

def _returns(values: list[float]) -> list[float]:
    rets = []
    for i in range(1, len(values)):
        prev = values[i - 1]
        if prev <= 0:
            continue
        rets.append((values[i] / prev) - 1.0)
    return rets

def _stdev(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = sum(xs) / len(xs)
    v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return sqrt(v)

def _atr_approx(closes: list[float], period: int) -> float:
    # ATR real requiere high/low; para MVP usamos abs delta de close como proxy estable
    if len(closes) < 2:
        return 0.0
    deltas = [abs(closes[i] - closes[i - 1]) for i in range(1, len(closes))]
    window = deltas[-period:] if len(deltas) >= period else deltas
    if not window:
        return 0.0
    return sum(window) / len(window)

def compute_features(last: float, closes: list[float]) -> Features:
    closes2 = closes[-max(settings.ema_long * 2, 300):] if closes else []
    if closes2 and last > 0:
        closes2 = closes2[:-1] + [last]

    ema_s = _ema(closes2, settings.ema_short) if closes2 else 0.0
    ema_l = _ema(closes2, settings.ema_long) if closes2 else 0.0

    rets = _returns(closes2[-settings.vol_window - 1:]) if closes2 else []
    vol = _stdev(rets)  # in return units
    vol_pct = float(vol)  # e.g. 0.04 == 4%

    atr = _atr_approx(closes2, settings.atr_period)
    regime = "SIDEWAYS"
    if ema_s > ema_l * 1.001:
        regime = "BULL"
    elif ema_s < ema_l * 0.999:
        regime = "BEAR"

    return Features(
        last=float(last),
        atr=float(atr),
        ema_short=float(ema_s),
        ema_long=float(ema_l),
        vol_pct=float(vol_pct),
        regime=regime,
    )
