from dataclasses import dataclass
from math import isnan

from app.providers.features import Features
from app.domain.signals import SignalKind

@dataclass
class Strategy:
    base_tp: float
    sl_pct: float
    trail_atr_mult: float
    profit_lock_pct: float
    cooldown_sec: int
    confirm_regime: bool

@dataclass
class Holding:
    id: int
    symbol: str
    entry: float
    invested_amount: float

@dataclass
class EngineState:
    trailing_active: bool
    trailing_anchor: float | None
    last_alert_ts: int | None

@dataclass
class Signal:
    kind: SignalKind
    message: str

def decide(now_ts: int, h: Holding, s: Strategy, f: Features, st: EngineState) -> list[Signal]:
    signals: list[Signal] = []

    if f.last <= 0 or isnan(f.last):
        return signals

    if st.last_alert_ts and (now_ts - st.last_alert_ts) < s.cooldown_sec:
        return signals

    pnl_pct = (f.last / h.entry) - 1.0

    # TP dinámico (estable)
    tp_threshold = s.base_tp + 0.5 * f.vol_pct
    if s.confirm_regime and f.regime != "BULL":
        tp_threshold *= 1.25

    # Activación trailing
    if (not st.trailing_active) and pnl_pct >= s.profit_lock_pct:
        st.trailing_active = True
        st.trailing_anchor = f.last

    # Trailing (prioridad alta)
    if st.trailing_active:
        st.trailing_anchor = max(st.trailing_anchor or f.last, f.last)
        trail_stop = (st.trailing_anchor or f.last) - (s.trail_atr_mult * f.atr)

        if f.last <= trail_stop:
            signals.append(Signal(
                kind=SignalKind.TRAILING_STOP,
                message=(
                    f"[{h.symbol}] Trailing stop tocado. "
                    f"Precio={f.last:.4f}, TrailStop≈{trail_stop:.4f}, PnL={pnl_pct*100:.2f}%."
                ),
            ))
            return signals

        # update informativo (se deduplica por bucket)
        signals.append(Signal(
            kind=SignalKind.TRAILING_UPDATE,
            message=(
                f"[{h.symbol}] Trailing activo. "
                f"Anchor={st.trailing_anchor:.4f}, Stop≈{trail_stop:.4f}, PnL={pnl_pct*100:.2f}%, Regime={f.regime}."
            ),
        ))
        return signals

    # SL inteligente (max fijo, soporte EMA - cushion)
    # usamos EMA short como soporte; en fase 2 puedes meter EMA de 4H/1D real
    smart_sl = max(h.entry * (1 - s.sl_pct), f.ema_short - 1.0 * f.atr)
    if f.last <= smart_sl:
        signals.append(Signal(
            kind=SignalKind.STOP_LOSS,
            message=(
                f"[{h.symbol}] Stop inteligente tocado. "
                f"Precio={f.last:.4f}, SL≈{smart_sl:.4f}, Regime={f.regime}."
            ),
        ))
        return signals

    # Take Profit si no hay trailing activo todavía
    if pnl_pct >= tp_threshold:
        signals.append(Signal(
            kind=SignalKind.TAKE_PROFIT,
            message=(
                f"[{h.symbol}] Umbral TP alcanzado. "
                f"Precio={f.last:.4f}, PnL={pnl_pct*100:.2f}%, TP≈{tp_threshold*100:.2f}%, Regime={f.regime}. "
                f"Sugerencia: toma parcial y activa trailing."
            ),
        ))

    return signals
