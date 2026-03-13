"""Security helpers: password hashing and JWT creation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext

from src.core.config import get_settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return _pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a stored hash."""
    return _pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def create_access_token(subject: str, expires_minutes: Optional[int] = None, extra_claims: Optional[dict[str, Any]] = None) -> str:
    """Create a signed JWT access token.

    Args:
        subject: token subject (typically user id as string).
        expires_minutes: optional expiry override in minutes.
        extra_claims: optional additional JWT claims.

    Returns:
        JWT string.
    """
    settings = get_settings()
    expire_minutes = expires_minutes if expires_minutes is not None else settings.access_token_expire_minutes
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expire_minutes)

    payload: dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
