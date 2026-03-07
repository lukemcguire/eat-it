"""FastAPI application entry point with lifespan context."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from eat_it.config import get_settings
from eat_it.database import get_session, init_db
from eat_it.routers.health import router as health_router
from eat_it.routers.ingredients import router as ingredients_router
from eat_it.routers.recipes import router as recipes_router
from eat_it.routers.search import router as search_router
from eat_it.routers.shopping_lists import router as shopping_lists_router
from eat_it.services.importer_registry import ImporterRegistry

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown.

    Startup:
        1. Initialize database (create tables if needed)
        2. Load embedding model from sentence_transformers
        3. Create ImporterRegistry and discover plugins

    Shutdown:
        SQLite handles connection cleanup automatically.
    """
    # Startup: Initialize database
    init_db()
    app.state.db_initialized = True
    logger.info("Database initialized")

    # Startup: Load embedding model
    settings = get_settings()
    try:
        from sentence_transformers import SentenceTransformer

        embedding_model = SentenceTransformer(settings.embedding_model)
        app.state.embedding_model = embedding_model
        logger.info(
            "Embedding model loaded: %s",
            settings.embedding_model,
        )
    except Exception:
        logger.exception("Failed to load embedding model")
        app.state.embedding_model = None

    # Startup: Create and populate importer registry
    importer_registry = ImporterRegistry()
    importer_registry.discover_plugins()
    app.state.importer_registry = importer_registry
    logger.info(
        "Importer registry initialized with %d plugins",
        len(importer_registry.get_importers()),
    )

    yield

    # Shutdown: Cleanup (SQLite handles connection cleanup automatically)
    logger.info("Application shutting down")


app = FastAPI(
    title="Eat It",
    version="0.1.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(health_router)
app.include_router(recipes_router, prefix="/recipes")
app.include_router(ingredients_router, prefix="/recipes", tags=["ingredients"])
app.include_router(search_router, tags=["search"])
app.include_router(shopping_lists_router, prefix="/shopping-lists")

# Serve static files in production (built frontend)
settings = get_settings()
static_dir = Path(settings.static_dir)
STATIC_DIR_EXISTS = static_dir.exists()

# API prefixes that should not be caught by SPA fallback
API_PREFIXES = ("/health", "/recipes", "/search", "/shopping-lists", "/docs", "/redoc", "/openapi.json")

if STATIC_DIR_EXISTS:
    app.mount(
        "/assets", StaticFiles(directory=static_dir / "assets"), name="assets"
    )


@app.get("/{full_path:path}")
async def serve_spa(full_path: str) -> FileResponse:
    """Serve index.html for client-side routing (SPA fallback).

    Only serves the SPA when static files exist (production mode).
    In development, the frontend dev server handles routing.
    """
    # Normalize path for matching (full_path doesn't include leading /)
    path_with_slash = f"/{full_path}"

    # Don't intercept API routes
    if path_with_slash.startswith(API_PREFIXES):
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")

    if not STATIC_DIR_EXISTS:
        # In development, return 404 - frontend dev server handles this
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(static_dir / "index.html")


# Expose session dependency for routes
__all__ = ["app", "get_session"]
