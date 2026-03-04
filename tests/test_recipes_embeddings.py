"""Tests for embedding generation in recipe CRUD operations.

These tests verify that:
- Recipes get embeddings on creation
- Embeddings are regenerated on update
- Embedding failures are silent (don't block saves)
- Recipes save even when embedding model is unavailable

The embedding model is mocked to avoid loading the heavy (~100MB)
sentence-transformers model during tests.
"""

from collections.abc import Generator
from contextlib import asynccontextmanager
from unittest.mock import MagicMock

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from eat_it.database import get_session
from eat_it.models import Recipe
from eat_it.routers.recipes import router as recipes_router


def _set_test_pragma(dbapi_connection, connection_record) -> None:  # noqa: ARG001
    """Set SQLite PRAGMA settings and load sqlite-vec on test connection."""
    dbapi_connection.enable_load_extension(True)
    import sqlite_vec

    sqlite_vec.load(dbapi_connection)

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    # Create the recipe_embeddings table for tests
    cursor = dbapi_connection.cursor()
    cursor.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS recipe_embeddings "
        "USING vec0(embedding FLOAT[384])"
    )
    cursor.close()


@asynccontextmanager
async def noop_lifespan(app: FastAPI):
    """No-op lifespan for testing that skips model loading."""
    yield


@pytest.fixture
def test_engine():
    """Create in-memory SQLite engine for testing with sqlite-vec."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine, "connect", _set_test_pragma)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine) -> Generator[Session, None, None]:
    """Yield a session from the test engine."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def mock_embedding_model():
    """Create a mock embedding model that returns predictable embeddings."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([0.1] * 384)
    return mock_model


@pytest.fixture
def client_with_embedding(test_engine, mock_embedding_model):
    """Create a TestClient with a mock embedding model in app.state."""
    test_app = FastAPI(
        title="Eat It Test",
        version="0.1.0",
        lifespan=noop_lifespan,
    )

    test_app.include_router(recipes_router, prefix="/recipes", tags=["recipes"])

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    test_app.dependency_overrides[get_session] = override_get_session

    with TestClient(test_app) as test_client:
        # Set mock embedding model in app state
        test_client.app.state.embedding_model = mock_embedding_model
        yield test_client

    test_app.dependency_overrides.clear()


@pytest.fixture
def client_without_embedding(test_engine):
    """Create a TestClient without an embedding model (embedding_model = None)."""
    test_app = FastAPI(
        title="Eat It Test",
        version="0.1.0",
        lifespan=noop_lifespan,
    )

    test_app.include_router(recipes_router, prefix="/recipes", tags=["recipes"])

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    test_app.dependency_overrides[get_session] = override_get_session

    with TestClient(test_app) as test_client:
        # Explicitly set embedding_model to None
        test_client.app.state.embedding_model = None
        yield test_client

    test_app.dependency_overrides.clear()


@pytest.fixture
def client_with_failing_embedding(test_engine):
    """Create a TestClient with an embedding model that raises on encode."""
    failing_model = MagicMock()
    failing_model.encode.side_effect = RuntimeError("Embedding failed!")

    test_app = FastAPI(
        title="Eat It Test",
        version="0.1.0",
        lifespan=noop_lifespan,
    )

    test_app.include_router(recipes_router, prefix="/recipes", tags=["recipes"])

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    test_app.dependency_overrides[get_session] = override_get_session

    with TestClient(test_app) as test_client:
        test_client.app.state.embedding_model = failing_model
        yield test_client

    test_app.dependency_overrides.clear()


class TestCreateRecipeWithEmbedding:
    """Tests for embedding generation during recipe creation."""

    def test_create_recipe_with_embedding(
        self, client_with_embedding, test_session
    ) -> None:
        """Recipe creation generates and stores embedding in recipe_embeddings."""
        # Create a recipe
        response = client_with_embedding.post(
            "/recipes/",
            json={
                "title": "Test Recipe",
                "description": "A test recipe",
                "instructions": "Mix and cook.",
            },
        )

        # Recipe should be created successfully
        assert response.status_code == 201
        recipe_id = response.json()["id"]

        # Verify embedding exists in recipe_embeddings table
        conn = test_session.connection().connection.dbapi_connection
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rowid FROM recipe_embeddings WHERE rowid = ?",
            [recipe_id],
        )
        row = cursor.fetchone()
        cursor.close()

        assert row is not None, "Embedding should be stored in recipe_embeddings"

    def test_update_recipe_regenerates_embedding(
        self, client_with_embedding, test_session
    ) -> None:
        """Recipe update regenerates embedding in recipe_embeddings table."""
        # Create a recipe with embedding
        create_response = client_with_embedding.post(
            "/recipes/",
            json={
                "title": "Original Title",
                "description": "Original description",
                "instructions": "Original instructions",
            },
        )
        assert create_response.status_code == 201
        recipe_id = create_response.json()["id"]

        # Update the recipe
        update_response = client_with_embedding.patch(
            f"/recipes/{recipe_id}",
            json={"title": "Updated Title"},
        )
        assert update_response.status_code == 200

        # Verify embedding still exists after update
        conn = test_session.connection().connection.dbapi_connection
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rowid FROM recipe_embeddings WHERE rowid = ?",
            [recipe_id],
        )
        row = cursor.fetchone()
        cursor.close()

        assert row is not None, "Embedding should still exist after update"


class TestEmbeddingSilentFailure:
    """Tests for silent embedding failure handling."""

    def test_create_recipe_without_embedding_model(
        self, client_without_embedding, test_session
    ) -> None:
        """Recipe is saved even when embedding model is None."""
        response = client_without_embedding.post(
            "/recipes/",
            json={
                "title": "Test Recipe",
                "description": "A test recipe",
                "instructions": "Mix and cook.",
            },
        )

        # Recipe should be created successfully despite no embedding model
        assert response.status_code == 201
        recipe_id = response.json()["id"]

        # Verify no embedding exists
        conn = test_session.connection().connection.dbapi_connection
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rowid FROM recipe_embeddings WHERE rowid = ?",
            [recipe_id],
        )
        row = cursor.fetchone()
        cursor.close()

        assert row is None, "No embedding should be stored when model is None"

    def test_embedding_generation_failure_is_silent(
        self, client_with_failing_embedding, test_session
    ) -> None:
        """Recipe is saved even when embedding generation raises an exception."""
        response = client_with_failing_embedding.post(
            "/recipes/",
            json={
                "title": "Test Recipe",
                "description": "A test recipe",
                "instructions": "Mix and cook.",
            },
        )

        # Recipe should be created successfully despite embedding failure
        assert response.status_code == 201
        recipe_id = response.json()["id"]

        # Verify no embedding exists (generation failed)
        conn = test_session.connection().connection.dbapi_connection
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rowid FROM recipe_embeddings WHERE rowid = ?",
            [recipe_id],
        )
        row = cursor.fetchone()
        cursor.close()

        assert row is None, "No embedding should be stored when generation fails"
