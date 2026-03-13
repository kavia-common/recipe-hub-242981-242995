"""Recipe endpoints (browse/search/view)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from src.db.session import get_db
from src.models import Favorite, Recipe, User
from src.schemas import RecipeCreate, RecipeOut, RecipeUpdate, UserPublic

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def _recipe_to_out(recipe: Recipe, favorites_count: int) -> RecipeOut:
    tags = [t.strip() for t in (recipe.tags_csv or "").split(",") if t.strip()]
    return RecipeOut(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        category=recipe.category,
        tags=tags,
        author=UserPublic.model_validate(recipe.author),
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        favorites_count=favorites_count,
    )


# PUBLIC_INTERFACE
@router.get(
    "",
    summary="List recipes (with optional search/category/tag filters)",
    description="Browse recipes with simple search and filtering. Returns a paginated list.",
    operation_id="list_recipes",
)
def list_recipes(
    q: Optional[str] = Query(None, description="Search query matched against title/description"),
    category: Optional[str] = Query(None, description="Category filter"),
    tag: Optional[str] = Query(None, description="Single tag filter (matches tags_csv contains)"),
    limit: int = Query(20, ge=1, le=50, description="Max number of recipes to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
) -> list[RecipeOut]:
    base = db.query(Recipe).options(joinedload(Recipe.author))

    if q:
        like = f"%{q.strip()}%"
        base = base.filter(or_(Recipe.title.ilike(like), Recipe.description.ilike(like)))
    if category:
        base = base.filter(Recipe.category == category)
    if tag:
        base = base.filter(Recipe.tags_csv.ilike(f"%{tag.strip()}%"))

    recipes = base.order_by(Recipe.created_at.desc()).limit(limit).offset(offset).all()
    if not recipes:
        return []

    recipe_ids = [r.id for r in recipes]
    counts = dict(
        db.query(Favorite.recipe_id, func.count(Favorite.id))
        .filter(Favorite.recipe_id.in_(recipe_ids))
        .group_by(Favorite.recipe_id)
        .all()
    )

    return [_recipe_to_out(r, int(counts.get(r.id, 0))) for r in recipes]


# PUBLIC_INTERFACE
@router.get(
    "/{recipe_id}",
    summary="Get recipe detail",
    description="Fetch a single recipe by id.",
    operation_id="get_recipe",
)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> RecipeOut:
    recipe = db.query(Recipe).options(joinedload(Recipe.author)).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    favorites_count = (
        db.query(func.count(Favorite.id)).filter(Favorite.recipe_id == recipe_id).scalar()
    ) or 0

    return _recipe_to_out(recipe, int(favorites_count))


# PUBLIC_INTERFACE
@router.post(
    "",
    summary="Create recipe (demo: assigns to demo user)",
    description="Creates a recipe. Minimal v1 uses the demo user as author if present.",
    operation_id="create_recipe",
)
def create_recipe(payload: RecipeCreate, db: Session = Depends(get_db)) -> RecipeOut:
    # Minimal v1: attach to demo user, else first user.
    author = db.query(User).order_by(User.id.asc()).first()
    if not author:
        raise HTTPException(status_code=409, detail="No users exist; seed the DB first.")

    recipe = Recipe(
        title=payload.title,
        description=payload.description,
        ingredients=payload.ingredients,
        instructions=payload.instructions,
        category=payload.category,
        tags_csv=",".join([t.strip() for t in payload.tags if t.strip()]) if payload.tags else None,
        author_id=author.id,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    recipe.author = author
    return _recipe_to_out(recipe, 0)


# PUBLIC_INTERFACE
@router.patch(
    "/{recipe_id}",
    summary="Update recipe (demo: no auth yet)",
    description="Updates recipe fields. Auth/ownership checks will be added in a later iteration.",
    operation_id="update_recipe",
)
def update_recipe(recipe_id: int, payload: RecipeUpdate, db: Session = Depends(get_db)) -> RecipeOut:
    recipe = db.query(Recipe).options(joinedload(Recipe.author)).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if payload.title is not None:
        recipe.title = payload.title
    if payload.description is not None:
        recipe.description = payload.description
    if payload.ingredients is not None:
        recipe.ingredients = payload.ingredients
    if payload.instructions is not None:
        recipe.instructions = payload.instructions
    if payload.category is not None:
        recipe.category = payload.category
    if payload.tags is not None:
        recipe.tags_csv = ",".join([t.strip() for t in payload.tags if t.strip()]) if payload.tags else None

    db.commit()
    db.refresh(recipe)

    favorites_count = (db.query(func.count(Favorite.id)).filter(Favorite.recipe_id == recipe_id).scalar()) or 0
    return _recipe_to_out(recipe, int(favorites_count))
