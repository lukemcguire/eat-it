"""Tests for search endpoint with semantic and keyword fallback.

Tests verify:
- Semantic search returns matching recipes with embeddings
- Keyword fallback when semantic returns no results
- Keyword fallback when embedding model is None
- Empty query returns 422 validation error
- Limit parameter is respected (max 20)
"""

from unittest.mock import MagicMock

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from eat_it.models.recipe import Recipe
from eat_it.services.embedding import serialize_f32


@pytest.fixture
def mock_embedding_model():
    """Create a mock embedding model for testing."""
    model = MagicMock()
    model.encode.return_value = np.array([0.1] * 384, dtype=np.float32)
    return model


@pytest.fixture
def client_with_model(client: TestClient, mock_embedding_model: MagicMock) -> TestClient:
    """Create a client with mock embedding model set."""
    client.app.state.embedding_model = mock_embedding_model
    return client


class TestSearchSemantic:
    """Tests for semantic search functionality."""

    def test_search_semantic_returns_results(
        self,
        client_with_model: TestClient,
        test_session: Session,
        mock_embedding_model: MagicMock,
    ) -> None:
        """Semantic search returns matching recipes with embeddings."""
        # Create a recipe
        recipe = Recipe(
            title="Pasta Carbonara",
            description="Classic Roman pasta dish",
            instructions="Cook pasta. Mix eggs and cheese.",
        )
        test_session.add(recipe)
        test_session.flush()

        # Insert embedding directly into recipe_embeddings table
        # Use the same vector that mock model returns for semantic match
        embedding = np.array([0.1] * 384, dtype=np.float32)
        embedding_binary = serialize_f32(embedding.tolist())
        conn = test_session.connection().connection.dbapi_connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recipe_embeddings(rowid, embedding) VALUES (?, ?)",
            [recipe.id, embedding_binary],
        )
        cursor.close()
        test_session.commit()

        # Search with matching query
        response = client_with_model.get("/search?q=pasta")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Pasta Carbonara"

    def test_search_keyword_fallback_no_semantic_results(
        self,
        client_with_model: TestClient,
        test_session: Session,
        mock_embedding_model: MagicMock,
    ) -> None:
        """Keyword fallback when semantic returns no results."""
        # Create a recipe
        recipe = Recipe(
            title="Spaghetti Bolognese",
            description="Italian meat sauce pasta",
            instructions="Cook spaghetti. Make sauce.",
        )
        test_session.add(recipe)
        test_session.flush()

        # Insert embedding with DIFFERENT vector (no semantic match)
        different_embedding = np.array([0.9] * 384, dtype=np.float32)
        embedding_binary = serialize_f32(different_embedding.tolist())
        conn = test_session.connection().connection.dbapi_connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recipe_embeddings(rowid, embedding) VALUES (?, ?)",
            [recipe.id, embedding_binary],
        )
        cursor.close()
        test_session.commit()

        # Mock model returns [0.1] * 384, very different from [0.9] * 384
        # So semantic search won't match, but keyword will
        response = client_with_model.get("/search?q=Spaghetti")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Spaghetti Bolognese"


class TestSearchKeywordFallback:
    """Tests for keyword fallback when model unavailable."""

    def test_search_keyword_fallback_no_model(
        self,
        client: TestClient,
        test_session: Session,
    ) -> None:
        """Keyword fallback when embedding model is None."""
        # Client fixture already sets embedding_model to None
        assert client.app.state.embedding_model is None

        # Create recipes (no embeddings needed for keyword search)
        recipe = Recipe(
            title="Chicken Stir Fry",
            description="Quick Asian dish",
            instructions="Stir fry chicken with vegetables.",
        )
        test_session.add(recipe)
        test_session.commit()

        # Search by keyword
        response = client.get("/search?q=Chicken")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Chicken Stir Fry"


class TestSearchValidation:
    """Tests for query validation."""

    def test_search_empty_query_validation(
        self,
        client: TestClient,
    ) -> None:
        """Empty query returns 422 Unprocessable Entity."""
        response = client.get("/search?q=")

        assert response.status_code == 422


class TestSearchLimit:
    """Tests for limit parameter."""

    def test_search_respects_limit(
        self,
        client: TestClient,
        test_session: Session,
    ) -> None:
        """Limit parameter is respected."""
        # Create 25 recipes with matching titles
        for i in range(25):
            recipe = Recipe(
                title=f"Test Recipe {i}",
                description="Test description",
                instructions="Test instructions.",
            )
            test_session.add(recipe)
        test_session.commit()

        # Request with limit=10
        response = client.get("/search?q=Test&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10

    def test_search_default_limit(
        self,
        client: TestClient,
        test_session: Session,
    ) -> None:
        """Default limit is 20."""
        # Create 25 recipes with matching titles
        for i in range(25):
            recipe = Recipe(
                title=f"Default Recipe {i}",
                description="Test description",
                instructions="Test instructions.",
            )
            test_session.add(recipe)
        test_session.commit()

        # Request without limit param (should default to 20)
        response = client.get("/search?q=Default")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 20
