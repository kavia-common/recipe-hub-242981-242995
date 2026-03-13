"""Schemas for recipes, categories, tags."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.common import ORMModel
from src.schemas.auth import UserOut


class CategoryOut(ORMModel):
    """Category output schema."""

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")


class TagOut(ORMModel):
    """Tag output schema."""

    id: int = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")


class RecipeCreateRequest(BaseModel):
    """Create recipe request."""

    title: str = Field(..., min_length=1, max_length=200, description="Recipe title")
    description: str = Field("", description="Short description")
    image_url: Optional[str] = Field(None, description="Optional image URL")

    ingredients: str = Field(..., description="Ingredients, free-form text (one per line recommended)")
    instructions: str = Field(..., description="Instructions, free-form text (steps recommended)")

    prep_minutes: int = Field(0, ge=0, description="Prep time in minutes")
    cook_minutes: int = Field(0, ge=0, description="Cook time in minutes")
    servings: int = Field(0, ge=0, description="Number of servings")

    is_public: bool = Field(True, description="Whether recipe is publicly visible")
    category_ids: list[int] = Field(default_factory=list, description="Category IDs to associate")
    tag_names: list[str] = Field(default_factory=list, description="Tag names to associate (created if missing)")


class RecipeUpdateRequest(BaseModel):
    """Update recipe request (partial updates supported)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Recipe title")
    description: Optional[str] = Field(None, description="Short description")
    image_url: Optional[str] = Field(None, description="Optional image URL")

    ingredients: Optional[str] = Field(None, description="Ingredients text")
    instructions: Optional[str] = Field(None, description="Instructions text")

    prep_minutes: Optional[int] = Field(None, ge=0, description="Prep time in minutes")
    cook_minutes: Optional[int] = Field(None, ge=0, description="Cook time in minutes")
    servings: Optional[int] = Field(None, ge=0, description="Number of servings")

    is_public: Optional[bool] = Field(None, description="Whether recipe is publicly visible")
    category_ids: Optional[list[int]] = Field(None, description="Category IDs to associate")
    tag_names: Optional[list[str]] = Field(None, description="Tag names to associate")


class RecipeOut(ORMModel):
    """Full recipe response."""

    id: int = Field(..., description="Recipe ID")
    title: str = Field(..., description="Title")
    description: str = Field(..., description="Description")
    image_url: Optional[str] = Field(None, description="Image URL")

    ingredients: str = Field(..., description="Ingredients")
    instructions: str = Field(..., description="Instructions")

    prep_minutes: int = Field(..., description="Prep minutes")
    cook_minutes: int = Field(..., description="Cook minutes")
    servings: int = Field(..., description="Servings")

    is_public: bool = Field(..., description="Public visibility")
    is_flagged: bool = Field(..., description="Flagged for moderation")

    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")

    author: UserOut = Field(..., description="Author")
    categories: list[CategoryOut] = Field(default_factory=list, description="Categories")
    tags: list[TagOut] = Field(default_factory=list, description="Tags")


class RecipeListItemOut(ORMModel):
    """Recipe summary for listing."""

    id: int = Field(..., description="Recipe ID")
    title: str = Field(..., description="Title")
    description: str = Field(..., description="Description")
    image_url: Optional[str] = Field(None, description="Image URL")
    prep_minutes: int = Field(..., description="Prep minutes")
    cook_minutes: int = Field(..., description="Cook minutes")
    servings: int = Field(..., description="Servings")
    is_public: bool = Field(..., description="Public visibility")
    is_flagged: bool = Field(..., description="Flagged for moderation")

    author: UserOut = Field(..., description="Author")
    categories: list[CategoryOut] = Field(default_factory=list, description="Categories")
    tags: list[TagOut] = Field(default_factory=list, description="Tags")
