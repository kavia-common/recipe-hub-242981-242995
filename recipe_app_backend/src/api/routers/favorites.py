"""Favorite recipes routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from src.api.deps import get_current_user
from src.core.db import get_db
from src.models.models import Favorite, Recipe, User
from src.schemas.lists import FavoriteOut

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get(
    "",
    response_model=list[FavoriteOut],
    summary="List my favorites",
    description="List recipes favorited by the authenticated user.",
)
def list_favorites(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[FavoriteOut]:
    """Return favorites for the current user."""
    items = (
        db.query(Favorite)
        .options(
            joinedload(Favorite.recipe)
            .joinedload(Recipe.author),
            joinedload(Favorite.recipe)
            .joinedload(Recipe.categories),
            joinedload(Favorite.recipe)
            .joinedload(Recipe.tags),
        )
        .filter(Favorite.user_id == user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return [FavoriteOut.model_validate(x) for x in items]


@router.post(
    "/{recipe_id}",
    response_model=dict,
    summary="Favorite a recipe",
    description="Adds a recipe to the authenticated user's favorites.",
)
def add_favorite(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Add a favorite for the current user."""
    recipe = db.get(Recipe, recipe_id)
    if not recipe or not recipe.is_public or recipe.is_flagged:
        raise HTTPException(status_code=404, detail="Recipe not found")

    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
        .first()
    )
    if existing:
        return {"ok": True}

    fav = Favorite(user_id=user.id, recipe_id=recipe_id)
    db.add(fav)
    db.commit()
    return {"ok": True}


@router.delete(
    "/{recipe_id}",
    response_model=dict,
    summary="Unfavorite a recipe",
    description="Removes a recipe from the authenticated user's favorites.",
)
def remove_favorite(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Remove a favorite for the current user."""
    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
    return {"ok": True}
