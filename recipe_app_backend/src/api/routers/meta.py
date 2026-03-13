"""Routes for categories and tags."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.models.models import Category, Tag
from src.schemas.recipes import CategoryOut, TagOut

router = APIRouter(prefix="/meta", tags=["Categories & Tags"])


@router.get(
    "/categories",
    response_model=list[CategoryOut],
    summary="List categories",
    description="Returns all categories for filtering and organization.",
)
def list_categories(db: Session = Depends(get_db)) -> list[CategoryOut]:
    """List all categories."""
    items = db.query(Category).order_by(Category.name.asc()).all()
    return [CategoryOut.model_validate(x) for x in items]


@router.get(
    "/tags",
    response_model=list[TagOut],
    summary="List tags",
    description="Returns all tags.",
)
def list_tags(db: Session = Depends(get_db)) -> list[TagOut]:
    """List all tags."""
    items = db.query(Tag).order_by(Tag.name.asc()).all()
    return [TagOut.model_validate(x) for x in items]
