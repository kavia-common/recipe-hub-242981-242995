"""Application configuration and environment variable access."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Strongly-typed app settings.

    Environment variables required:
    - DATABASE_URL: PostgreSQL connection string (e.g. postgresql+psycopg2://user:pass@host:5432/db)
    - JWT_SECRET_KEY: secret for signing JWTs
    - JWT_ALGORITHM: optional, defaults to HS256
    - ACCESS_TOKEN_EXPIRE_MINUTES: optional, defaults to 60
    """

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Load settings from environment variables.

    Returns:
        Settings: loaded settings.

    Raises:
        RuntimeError: if required variables are missing.
    """
    database_url = os.getenv("DATABASE_URL", "").strip()
    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "").strip()

    if not database_url:
        raise RuntimeError("Missing required env var DATABASE_URL")
    if not jwt_secret_key:
        raise RuntimeError("Missing required env var JWT_SECRET_KEY")

    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256").strip() or "HS256"
    try:
        access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    except ValueError:
        access_token_expire_minutes = 60

    return Settings(
        database_url=database_url,
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=jwt_algorithm,
        access_token_expire_minutes=access_token_expire_minutes,
    )
