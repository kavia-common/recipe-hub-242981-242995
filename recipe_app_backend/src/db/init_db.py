"""Database initialization utilities."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.db.base import Base
from src.db.session import ENGINE
from src.models import Recipe, User
from src.core.security import hash_password


# PUBLIC_INTERFACE
def create_all_tables() -> None:
    """Create all database tables.

    Note: For production, use migrations (Alembic). This is a minimal bootstrap.
    """
    Base.metadata.create_all(bind=ENGINE)


# PUBLIC_INTERFACE
def seed_demo_data(db: Session) -> None:
    """Seed the database with a demo user and a few recipes if empty."""
    has_user = db.query(User).limit(1).first()
    if has_user:
        return

    demo = User(
        email="demo@recipehub.local",
        username="demo",
        password_hash=hash_password("demo1234"),
        is_admin=True,
    )
    db.add(demo)
    db.flush()

    recipes = [
        Recipe(
            title="Retro PB&J Deluxe",
            description="A nostalgic classic with a tiny twist.",
            ingredients="2 slices bread\n2 tbsp peanut butter\n2 tbsp strawberry jam\n1 tsp honey (optional)\nPinch of sea salt",
            instructions="1) Toast bread lightly.\n2) Spread peanut butter on one slice.\n3) Spread jam on the other.\n4) Drizzle honey and add a pinch of salt.\n5) Assemble, slice, enjoy.",
            category="Snacks",
            tags_csv="retro,quick,kid-friendly",
            author_id=demo.id,
        ),
        Recipe(
            title="Neon Noodle Bowl",
            description="Bright, comforting noodles with a punchy sauce.",
            ingredients="200g noodles\n2 tbsp soy sauce\n1 tbsp sesame oil\n1 tsp chili flakes\n1 clove garlic (minced)\nGreen onions",
            instructions="1) Cook noodles.\n2) Mix sauce ingredients.\n3) Toss noodles with sauce.\n4) Top with green onions.",
            category="Dinner",
            tags_csv="noodles,spicy,comfort",
            author_id=demo.id,
        ),
    ]
    db.add_all(recipes)
    db.commit()
