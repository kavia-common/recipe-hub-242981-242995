"""Schemas related to authentication and users."""

from pydantic import BaseModel, Field, EmailStr

from src.schemas.common import ORMModel


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class RegisterRequest(BaseModel):
    """User registration payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")
    display_name: str = Field(..., min_length=1, max_length=120, description="Display name")


class LoginRequest(BaseModel):
    """Login payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserOut(ORMModel):
    """User data safe for returning to client."""

    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    display_name: str = Field(..., description="Display name")
    is_admin: bool = Field(..., description="Whether user is admin")
