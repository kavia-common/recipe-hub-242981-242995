"""Database session and engine helpers."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PUBLIC_INTERFACE
def get_db():
    """FastAPI dependency that yields a SQLAlchemy session and ensures it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
