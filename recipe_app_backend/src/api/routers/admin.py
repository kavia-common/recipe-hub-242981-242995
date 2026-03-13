"""Admin moderation routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from src.api.deps import require_admin
from src.core.db import get_db
from src.models.models import ModerationLog, Recipe, User
from src.schemas.recipes import RecipeListItemOut

router = APIRouter(prefix="/admin", tags=["Admin/Moderation"])


@router.get(
    "/flagged",
    response_model=list[RecipeListItemOut],
    summary="List flagged recipes",
    description="Admin-only: list flagged recipes for moderation.",
)
def list_flagged(db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> list[RecipeListItemOut]:
    """List flagged recipes (admin)."""
    _ = admin
    items = (
        db.query(Recipe)
        .options(joinedload(Recipe.author), joinedload(Recipe.categories), joinedload(Recipe.tags))
        .filter(Recipe.is_flagged.is_(True))
        .order_by(Recipe.updated_at.desc())
        .limit(200)
        .all()
    )
    return [RecipeListItemOut.model_validate(x) for x in items]


@router.post(
    "/flag/{recipe_id}",
    response_model=dict,
    summary="Flag a recipe",
    description="Admin-only: flag a recipe (hides it from public browsing).",
)
def flag_recipe(
    recipe_id: int,
    note: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    """Flag a recipe."""
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.is_flagged = True
    recipe.updated_at = datetime.utcnow()
    db.add(recipe)
    db.add(
        ModerationLog(
            admin_user_id=admin.id,
            action="flag",
            recipe_id=recipe_id,
            note=note or "",
        )
    )
    db.commit()
    return {"ok": True}


@router.post(
    "/unflag/{recipe_id}",
    response_model=dict,
    summary="Unflag a recipe",
    description="Admin-only: unflag a recipe (restores public visibility if public).",
)
def unflag_recipe(
    recipe_id: int,
    note: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    """Unflag a recipe."""
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.is_flagged = False
    recipe.updated_at = datetime.utcnow()
    db.add(recipe)
    db.add(
        ModerationLog(
            admin_user_id=admin.id,
            action="unflag",
            recipe_id=recipe_id,
            note=note or "",
        )
    )
    db.commit()
    return {"ok": True}


@router.delete(
    "/recipes/{recipe_id}",
    response_model=dict,
    summary="Delete a recipe",
    description="Admin-only: deletes a recipe (and related favorites).",
)
def delete_recipe(
    recipe_id: int,
    note: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    """Delete a recipe."""
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(recipe)
    db.add(
        ModerationLog(
            admin_user_id=admin.id,
            action="delete",
            recipe_id=recipe_id,
            note=note or "",
        )
    )
    db.commit()
    return {"ok": True}
