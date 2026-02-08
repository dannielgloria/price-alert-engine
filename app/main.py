from fastapi import FastAPI
from app.observability.logging import configure_logging
from app.persistence.db import init_db

from app.api.routes_health import router as health_router
from app.api.routes_assets import router as assets_router
from app.api.routes_holdings import router as holdings_router
from app.api.routes_strategies import router as strategies_router

def create_app() -> FastAPI:
    configure_logging()
    init_db()

    app = FastAPI(title="Price Alert Engine", version="0.1.0")
    app.include_router(health_router)
    app.include_router(assets_router, prefix="/assets", tags=["assets"])
    app.include_router(holdings_router, prefix="/holdings", tags=["holdings"])
    app.include_router(strategies_router, prefix="/strategies", tags=["strategies"])
    return app

app = create_app()
