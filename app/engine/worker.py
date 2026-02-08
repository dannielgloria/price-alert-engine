import time
import logging
from sqlalchemy.orm import Session

from app.persistence.repo import Repo
from app.providers.aggregator import ProviderAggregator
from app.providers.features import compute_features
from app.engine.decision import decide, Strategy as DStrategy, Holding as DHolding, EngineState as DState
from app.notify.telegram import TelegramNotifier
from app.domain.signals import SignalKind

log = logging.getLogger("worker")

class Worker:
    def __init__(self, db: Session):
        self.repo = Repo(db)
        self.providers = ProviderAggregator()
        self.notifier = TelegramNotifier()

    async def tick(self) -> None:
        now_ts = int(time.time())
        assets = self.repo.list_enabled_assets()

        for a in assets:
            asset_dict = {
                "symbol": a.symbol,
                "binance_symbol": a.binance_symbol,
                "coinbase_product_id": a.coinbase_product_id,
                "coingecko_id": a.coingecko_id,
            }

            holdings = self.repo.list_holdings(a.symbol)
            if not holdings:
                continue

            try:
                pp = await self.providers.get_pricepoint(asset_dict)
                f = compute_features(pp.last, pp.ohlcv_close)
            except Exception as e:
                log.warning("price/features failed for %s: %s", a.symbol, e)
                continue

            s = self.repo.get_or_create_strategy(a.symbol)
            ds = DStrategy(
                base_tp=s.base_tp,
                sl_pct=s.sl_pct,
                trail_atr_mult=s.trail_atr_mult,
                profit_lock_pct=s.profit_lock_pct,
                cooldown_sec=s.cooldown_sec,
                confirm_regime=s.confirm_regime,
            )

            for h in holdings:
                st = self.repo.load_state(h.id)
                dst = DState(
                    trailing_active=st.trailing_active,
                    trailing_anchor=st.trailing_anchor,
                    last_alert_ts=st.last_alert_ts,
                )

                dh = DHolding(id=h.id, symbol=h.symbol, entry=h.entry, invested_amount=h.invested_amount)

                signals = decide(now_ts, dh, ds, f, dst)

                for sig in signals:
                    if self.repo.should_send_alert(h.id, sig.kind, now_ts):
                        await self.notifier.send(sig.message)
                        self.repo.record_alert(h.id, sig.kind, sig.message, now_ts)
                        dst.last_alert_ts = now_ts

                # persist state back
                st.trailing_active = dst.trailing_active
                st.trailing_anchor = dst.trailing_anchor
                st.last_alert_ts = dst.last_alert_ts
                self.repo.save_state(st)
