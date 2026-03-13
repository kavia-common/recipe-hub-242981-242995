"""Database session management (SQLAlchemy)."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import get_settings

_settings = None


def _get_engine():
    global _settings
    if _settings is None:
        _settings = get_settings()
    # pool_pre_ping helps avoid stale connections.
    return create_engine(_settings.database_url, pool_pre_ping=True)


ENGINE = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


# PUBLIC_INTERFACE
def get_db() -> Session:
    """FastAPI dependency that yields a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
