"""Pytest configuration and fixtures for testing."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
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
    """Set SQLite PRAGMA settings on test connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def test_engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")

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


@pytest.fixture
def client(test_session: Session) -> Generator[TestClient, None, None]:
    """Create a TestClient with overridden session dependency.

    Note: This requires the app to have a get_session dependency.
    For now, this fixture provides the test_session for manual override.
    """
    from eat_it.main import app
    from eat_it.database import get_session

    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
