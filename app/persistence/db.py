from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.settings import settings

class Base(DeclarativeBase):
    pass

_engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

def init_db() -> None:
    # Import models to register metadata
    from app.domain import models  # noqa: F401
    Base.metadata.create_all(bind=_engine)
