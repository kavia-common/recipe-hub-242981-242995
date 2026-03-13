"""Recipe CRUD and browsing routes."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from src.api.deps import get_current_user
from src.core.db import get_db
from src.models.models import Category, Recipe, Tag, User
from src.schemas.recipes import RecipeCreateRequest, RecipeListItemOut, RecipeOut, RecipeUpdateRequest

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def _recipe_query_base(db: Session):
    """Internal helper: common recipe query with eager loads."""
    return (
        db.query(Recipe)
        .options(joinedload(Recipe.author), joinedload(Recipe.categories), joinedload(Recipe.tags))
    )


@router.get(
    "",
    response_model=list[RecipeListItemOut],
    summary="Browse/search recipes",
    description="Browse public recipes with optional search query, category filter, and tag filter.",
)
def list_recipes(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search query (matches title/description)"),
    category_id: Optional[int] = Query(None, description="Filter by category id"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    include_flagged: bool = Query(False, description="Include flagged recipes (admin use)"),
) -> list[RecipeListItemOut]:
    """List public recipes with optional search/filter."""
    query = _recipe_query_base(db).filter(Recipe.is_public.is_(True))

    if not include_flagged:
        query = query.filter(Recipe.is_flagged.is_(False))

    if q:
        like = f"%{q.strip()}%"
        query = query.filter((Recipe.title.ilike(like)) | (Recipe.description.ilike(like)))

    if category_id is not None:
        query = query.join(Recipe.categories).filter(Category.id == category_id)

    if tag:
        query = query.join(Recipe.tags).filter(Tag.name.ilike(tag.strip()))

    items = query.order_by(Recipe.created_at.desc()).limit(100).all()
    return [RecipeListItemOut.model_validate(x) for x in items]


@router.get(
    "/{recipe_id}",
    response_model=RecipeOut,
    summary="Get recipe details",
    description="Returns a recipe by id, including ingredients/instructions.",
)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> RecipeOut:
    """Get a single public recipe by ID."""
    recipe = _recipe_query_base(db).filter(Recipe.id == recipe_id).first()
    if not recipe or (not recipe.is_public):
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.is_flagged:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RecipeOut.model_validate(recipe)


@router.post(
    "",
    response_model=RecipeOut,
    summary="Create personal recipe",
    description="Create a new recipe owned by the authenticated user.",
)
def create_recipe(
    payload: RecipeCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RecipeOut:
    """Create a recipe for the current user."""
    categories = []
    if payload.category_ids:
        categories = db.query(Category).filter(Category.id.in_(payload.category_ids)).all()

    tags = []
    for name in payload.tag_names:
        clean = name.strip()
        if not clean:
            continue
        tag = db.query(Tag).filter(Tag.name.ilike(clean)).first()
        if not tag:
            tag = Tag(name=clean)
            db.add(tag)
            db.flush()
        tags.append(tag)

    recipe = Recipe(
        title=payload.title,
        description=payload.description,
        image_url=payload.image_url,
        ingredients=payload.ingredients,
        instructions=payload.instructions,
        prep_minutes=payload.prep_minutes,
        cook_minutes=payload.cook_minutes,
        servings=payload.servings,
        is_public=payload.is_public,
        author_id=user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    recipe.categories = categories
    recipe.tags = tags

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    recipe = _recipe_query_base(db).filter(Recipe.id == recipe.id).first()
    return RecipeOut.model_validate(recipe)


@router.put(
    "/{recipe_id}",
    response_model=RecipeOut,
    summary="Update personal recipe",
    description="Update a recipe owned by the authenticated user (or admin).",
)
def update_recipe(
    recipe_id: int,
    payload: RecipeUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RecipeOut:
    """Update a recipe owned by current user (or admin)."""
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")

    for field in [
        "title",
        "description",
        "image_url",
        "ingredients",
        "instructions",
        "prep_minutes",
        "cook_minutes",
        "servings",
        "is_public",
    ]:
        value = getattr(payload, field)
        if value is not None:
            setattr(recipe, field, value)

    if payload.category_ids is not None:
        categories = []
        if payload.category_ids:
            categories = db.query(Category).filter(Category.id.in_(payload.category_ids)).all()
        recipe.categories = categories

    if payload.tag_names is not None:
        tags = []
        for name in payload.tag_names:
            clean = name.strip()
            if not clean:
                continue
            tag = db.query(Tag).filter(Tag.name.ilike(clean)).first()
            if not tag:
                tag = Tag(name=clean)
                db.add(tag)
                db.flush()
            tags.append(tag)
        recipe.tags = tags

    recipe.updated_at = datetime.utcnow()
    db.add(recipe)
    db.commit()

    recipe_full = _recipe_query_base(db).filter(Recipe.id == recipe_id).first()
    return RecipeOut.model_validate(recipe_full)


@router.get(
    "/mine/list",
    response_model=list[RecipeListItemOut],
    summary="List my recipes",
    description="List recipes created by the authenticated user.",
)
def list_my_recipes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[RecipeListItemOut]:
    """List recipes owned by current user."""
    items = (
        _recipe_query_base(db)
        .filter(and_(Recipe.author_id == user.id, Recipe.is_flagged.is_(False)))
        .order_by(Recipe.updated_at.desc())
        .limit(200)
        .all()
    )
    return [RecipeListItemOut.model_validate(x) for x in items]
