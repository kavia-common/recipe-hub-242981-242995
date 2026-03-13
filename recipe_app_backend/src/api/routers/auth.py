"""Authentication routes: register and login."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.core.db import get_db
from src.core.security import create_access_token, hash_password, verify_password
from src.models.models import User
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserOut,
    summary="Register a new user",
    description="Creates a new user account with email + password.",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserOut:
    """Register a new user with email/password and return the created user."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Validates credentials and returns a JWT access token.",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Login a user and return an access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(user.id), extra_claims={"is_admin": user.is_admin})
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user",
    description="Returns the current authenticated user's profile.",
)
def me(user: User = Depends(get_current_user)) -> UserOut:
    """Return the currently authenticated user."""
    return UserOut.model_validate(user)
