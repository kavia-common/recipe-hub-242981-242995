"""
FastAPI entrypoint for Recipe Hub.

Exposes REST endpoints for:
- Authentication
- Recipe browsing/search + detail
- Favorites
- Shopping list
- Categories/tags metadata
- Admin moderation

Returns:
    FastAPI app instance for Uvicorn.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import admin, auth, favorites, meta, recipes, shopping_list
from src.core.config import settings

openapi_tags = [
    {"name": "Auth", "description": "User registration, login, and current user profile."},
    {"name": "Recipes", "description": "Browse/search recipes, view details, and manage personal recipes."},
    {"name": "Favorites", "description": "Save/unsave favorite recipes."},
    {"name": "Shopping List", "description": "Generate and manage shopping list items."},
    {"name": "Categories & Tags", "description": "Metadata for filtering recipes."},
    {"name": "Admin/Moderation", "description": "Admin tools for moderating flagged content."},
    {"name": "System", "description": "Health and system endpoints."},
]

app = FastAPI(
    title=settings.APP_NAME,
    description="Recipe Hub API for browsing, saving, and managing recipes.",
    version=settings.APP_VERSION,
    openapi_tags=openapi_tags,
)

origins = [x.strip() for x in settings.ALLOWED_ORIGINS.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[x.strip() for x in settings.ALLOWED_METHODS.split(",") if x.strip()],
    allow_headers=[x.strip() for x in settings.ALLOWED_HEADERS.split(",") if x.strip()],
)

app.include_router(auth.router)
app.include_router(meta.router)
app.include_router(recipes.router)
app.include_router(favorites.router)
app.include_router(shopping_list.router)
app.include_router(admin.router)


@app.get(
    "/healthz",
    tags=["System"],
    summary="Health check",
    description="Simple health endpoint for uptime checks.",
)
def healthz() -> dict:
    """Return service health status."""
    return {"ok": True}
