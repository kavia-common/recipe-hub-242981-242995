"""Schemas for favorites and shopping lists."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.common import ORMModel
from src.schemas.recipes import RecipeListItemOut


class FavoriteOut(ORMModel):
    """Favorite record."""

    id: int = Field(..., description="Favorite ID")
    created_at: datetime = Field(..., description="Created at")
    recipe: RecipeListItemOut = Field(..., description="Favorited recipe")


class AddShoppingListItemsRequest(BaseModel):
    """Add items to shopping list (bulk)."""

    items: list[str] = Field(..., min_length=1, description="List of item text lines")


class ShoppingListItemOut(ORMModel):
    """Shopping list item."""

    id: int = Field(..., description="Item ID")
    text: str = Field(..., description="Text")
    is_checked: bool = Field(..., description="Checked")
    created_at: datetime = Field(..., description="Created at")


class ToggleShoppingItemRequest(BaseModel):
    """Toggle checked state."""

    is_checked: bool = Field(..., description="New checked state")
