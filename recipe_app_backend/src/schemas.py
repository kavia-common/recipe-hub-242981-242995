"""Pydantic schemas for Recipe Hub API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    """Public user profile returned by APIs."""

    id: int = Field(..., description="User id")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="User handle")
    is_admin: bool = Field(..., description="Whether the user is an admin")

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    """Common recipe fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Recipe title")
    description: Optional[str] = Field(None, description="Short description")
    ingredients: str = Field(..., min_length=1, description="Ingredients, free-form text")
    instructions: str = Field(..., min_length=1, description="Instructions, free-form text")
    category: Optional[str] = Field(None, max_length=64, description="Category name (simple v1)")
    tags: list[str] = Field(default_factory=list, description="Tags (simple v1)")


class RecipeCreate(RecipeBase):
    """Payload to create a recipe."""
    pass


class RecipeUpdate(BaseModel):
    """Payload to update a recipe (partial)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Recipe title")
    description: Optional[str] = Field(None, description="Short description")
    ingredients: Optional[str] = Field(None, min_length=1, description="Ingredients, free-form text")
    instructions: Optional[str] = Field(None, min_length=1, description="Instructions, free-form text")
    category: Optional[str] = Field(None, max_length=64, description="Category name (simple v1)")
    tags: Optional[list[str]] = Field(None, description="Tags (simple v1)")


class RecipeOut(RecipeBase):
    """Recipe returned by APIs."""

    id: int = Field(..., description="Recipe id")
    author: UserPublic = Field(..., description="Recipe author")
    created_at: datetime = Field(..., description="Created timestamp (UTC)")
    updated_at: datetime = Field(..., description="Updated timestamp (UTC)")
    favorites_count: int = Field(..., description="Number of favorites")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
