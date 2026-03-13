"""FastAPI entrypoint for Recipe Hub backend.

Exposes REST endpoints for browsing/searching/viewing recipes and minimal authentication.

Environment variables required:
- DATABASE_URL
- JWT_SECRET_KEY
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.init_db import create_all_tables, seed_demo_data
from src.db.session import SessionLocal
from src.api.routes.auth import router as auth_router
from src.api.routes.recipes import router as recipes_router

openapi_tags = [
    {"name": "System", "description": "Health and system endpoints."},
    {"name": "Recipes", "description": "Browse/search/view and manage recipes."},
    {"name": "Auth", "description": "Authentication endpoints (JWT)."},
]

app = FastAPI(
    title="Recipe Hub API",
    description="Recipe Hub backend API for browsing/searching recipes, favorites, shopping lists, and user accounts.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend origin(s).
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    """Initialize database tables and seed demo data (minimal bootstrap)."""
    create_all_tables()
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["System"],
    summary="Health check",
    description="Simple health check endpoint.",
    operation_id="health_check",
)
def health_check():
    """Return a minimal health response."""
    return {"message": "Healthy"}


app.include_router(recipes_router)
app.include_router(auth_router)
