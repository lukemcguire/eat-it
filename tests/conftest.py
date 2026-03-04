"""Pytest configuration and fixtures for testing."""

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# Import models to ensure they're registered with SQLModel.metadata
from eat_it.models import (  # noqa: F401
    Ingredient,
    IngredientGroup,
    Recipe,
    Settings,
    ShoppingList,
    ShoppingListItem,
)


def _set_test_pragma(dbapi_connection, connection_record) -> None:  # noqa: ARG001
    """Set SQLite PRAGMA settings and load sqlite-vec on test connection."""
    # Load sqlite-vec extension for vector search support
    dbapi_connection.enable_load_extension(True)
    import sqlite_vec

    sqlite_vec.load(dbapi_connection)

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    # Create the recipe_embeddings virtual table for semantic search tests
    cursor = dbapi_connection.cursor()
    cursor.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS recipe_embeddings "
        "USING vec0(embedding FLOAT[384])"
    )
    cursor.close()


@pytest.fixture
def test_engine():
    """Create in-memory SQLite engine for testing.

    Uses StaticPool to reuse the same connection, which is needed for
    FastAPI TestClient running in a thread pool with in-memory SQLite.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Apply PRAGMA settings on connect
    event.listen(engine, "connect", _set_test_pragma)

    # Create all tables
    SQLModel.metadata.create_all(engine)

    return engine


@pytest.fixture
def test_session(test_engine) -> Generator[Session, None, None]:
    """Yield a session from the test engine."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(autouse=True)
def clean_database(test_engine):
    """Clear all tables before each test for isolation.

    This fixture runs automatically before each test to ensure
    database isolation when using StaticPool with in-memory database.
    """
    from sqlmodel import delete

    with Session(test_engine) as session:
        # Delete in order of foreign key dependencies
        session.exec(delete(Ingredient))  # type: ignore
        session.exec(delete(IngredientGroup))  # type: ignore
        session.exec(delete(ShoppingListItem))  # type: ignore
        session.exec(delete(ShoppingList))  # type: ignore
        session.exec(delete(Recipe))  # type: ignore
        session.exec(delete(Settings))  # type: ignore
        session.commit()
    yield


@asynccontextmanager
async def noop_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """No-op lifespan for testing that skips model loading."""
    yield


@pytest.fixture
def client(test_engine) -> Generator[TestClient, None, None]:
    """Create a TestClient with overridden session dependency.

    Uses a no-op lifespan to avoid loading the embedding model during tests.
    Uses the test_engine with StaticPool for thread-safe in-memory SQLite.
    """
    from eat_it.database import get_session
    from eat_it.routers.health import router as health_router
    from eat_it.routers.recipes import router as recipes_router

    # Create a test app without the heavy lifespan
    test_app = FastAPI(
        title="Eat It Test",
        version="0.1.0",
        lifespan=noop_lifespan,
    )

    # Include the same routers
    test_app.include_router(health_router)
    test_app.include_router(recipes_router, prefix="/recipes", tags=["recipes"])

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    test_app.dependency_overrides[get_session] = override_get_session

    with TestClient(test_app) as test_client:
        # Set embedding_model to None for tests (no model loaded)
        test_client.app.state.embedding_model = None
        yield test_client

    test_app.dependency_overrides.clear()
