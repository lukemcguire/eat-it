"""FastAPI application entry point with lifespan context."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from eat_it.config import get_settings
from eat_it.database import get_session, init_db
from eat_it.routers.health import router as health_router
from eat_it.routers.recipes import router as recipes_router
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

# Expose session dependency for routes
__all__ = ["app", "get_session"]
