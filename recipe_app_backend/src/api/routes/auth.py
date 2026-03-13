"""Authentication endpoints (minimal v1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.security import create_access_token, verify_password
from src.db.session import get_db
from src.models import User
from src.schemas import TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    """Login request payload."""

    username_or_email: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


# PUBLIC_INTERFACE
@router.post(
    "/login",
    summary="Login (returns JWT)",
    description="Minimal v1 login using username/email + password, returning a JWT.",
    operation_id="login",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = (
        db.query(User)
        .filter((User.username == payload.username_or_email) | (User.email == payload.username_or_email))
        .first()
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id), extra_claims={"username": user.username, "is_admin": user.is_admin})
    return TokenResponse(access_token=token, token_type="bearer")
