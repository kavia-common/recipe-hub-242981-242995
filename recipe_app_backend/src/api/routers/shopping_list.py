"""Shopping list routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.core.db import get_db
from src.models.models import Recipe, ShoppingListItem, User
from src.schemas.lists import (
    AddShoppingListItemsRequest,
    ShoppingListItemOut,
    ToggleShoppingItemRequest,
)

router = APIRouter(prefix="/shopping-list", tags=["Shopping List"])


def _split_ingredients(text: str) -> list[str]:
    """Internal helper to normalize ingredient text into lines."""
    lines = []
    for raw in text.splitlines():
        clean = raw.strip(" \t-•")
        if clean:
            lines.append(clean)
    return lines


@router.get(
    "",
    response_model=list[ShoppingListItemOut],
    summary="Get my shopping list",
    description="Returns the authenticated user's shopping list items.",
)
def get_list(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ShoppingListItemOut]:
    """Get shopping list items for current user."""
    items = (
        db.query(ShoppingListItem)
        .filter(ShoppingListItem.user_id == user.id)
        .order_by(ShoppingListItem.created_at.desc())
        .limit(500)
        .all()
    )
    return [ShoppingListItemOut.model_validate(x) for x in items]


@router.post(
    "/add",
    response_model=dict,
    summary="Add shopping list items",
    description="Adds one or more items to the authenticated user's shopping list.",
)
def add_items(
    payload: AddShoppingListItemsRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Add items to shopping list."""
    for item in payload.items:
        clean = item.strip()
        if not clean:
            continue
        db.add(ShoppingListItem(user_id=user.id, text=clean, is_checked=False))
    db.commit()
    return {"ok": True}


@router.post(
    "/from-recipe/{recipe_id}",
    response_model=dict,
    summary="Generate items from a recipe",
    description="Parses the recipe ingredients into lines and appends them to the user's shopping list.",
)
def add_from_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Add shopping list items from a recipe's ingredients text."""
    recipe = db.get(Recipe, recipe_id)
    if not recipe or not recipe.is_public or recipe.is_flagged:
        raise HTTPException(status_code=404, detail="Recipe not found")

    items = _split_ingredients(recipe.ingredients)
    for item in items:
        db.add(ShoppingListItem(user_id=user.id, text=item, is_checked=False))
    db.commit()
    return {"ok": True, "added": len(items)}


@router.patch(
    "/{item_id}",
    response_model=dict,
    summary="Toggle shopping list item",
    description="Sets the checked state for a shopping list item.",
)
def toggle_item(
    item_id: int,
    payload: ToggleShoppingItemRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Toggle a shopping list item for current user."""
    item = db.get(ShoppingListItem, item_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_checked = payload.is_checked
    db.add(item)
    db.commit()
    return {"ok": True}


@router.delete(
    "/{item_id}",
    response_model=dict,
    summary="Delete shopping list item",
    description="Deletes a shopping list item.",
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Delete a shopping list item."""
    item = db.get(ShoppingListItem, item_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
