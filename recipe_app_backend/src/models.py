"""ORM models for Recipe Hub.

This file keeps the first iteration simple; can be split into a models/ package later.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class TimestampMixin:
    """Common created/updated timestamps."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class User(Base, TimestampMixin):
    """Application user account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="author", cascade="all, delete-orphan")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    shopping_lists: Mapped[list["ShoppingList"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Recipe(Base, TimestampMixin):
    """A recipe created by a user."""

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ingredients: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    author: Mapped["User"] = relationship(back_populates="recipes")

    category: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    tags_csv: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # simple v1: comma-separated

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")


class Favorite(Base, TimestampMixin):
    """A user favoriting a recipe."""

    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_recipe"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorites")
    recipe: Mapped["Recipe"] = relationship(back_populates="favorites")


class ShoppingList(Base, TimestampMixin):
    """Shopping list generated/curated by a user."""

    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False, default="My Shopping List")
    items: Mapped[str] = mapped_column(Text, nullable=False, default="")  # simple v1: newline-separated

    user: Mapped["User"] = relationship(back_populates="shopping_lists")
