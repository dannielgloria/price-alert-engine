import asyncio
import time
import logging

from app.observability.logging import configure_logging
from app.persistence.db import SessionLocal, init_db
from app.settings import settings
from app.engine.worker import Worker

async def main() -> None:
    configure_logging()
    log = logging.getLogger("run")
    init_db()

    while True:
        log.info("🔥 Worker tick starting...")
        start = time.time()
        db = SessionLocal()
        try:
            log.info("Scanning assets...")
            w = Worker(db)
            await w.tick()
        except Exception as e:
            log.exception("worker tick failed: %s", e)
        finally:
            db.close()

        elapsed = time.time() - start
        sleep_for = max(0.0, float(settings.poll_interval_sec) - elapsed)
        await asyncio.sleep(sleep_for)

if __name__ == "__main__":
    asyncio.run(main())
