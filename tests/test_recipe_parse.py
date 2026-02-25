"""Tests for /recipes/parse endpoint."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlmodel import Session

from eat_it.models.recipe import Recipe
from eat_it.services.recipe_parser import ParseError, ParseErrorCode, ParseResult


@pytest.fixture
def mock_parser(mocker):
    """Mock RecipeParser.parse_url method."""
    mock = mocker.patch(
        "eat_it.routers.recipes.RecipeParser.parse_url",
        new_callable=AsyncMock,
    )
    return mock


def test_parse_recipe_success(client, mock_parser) -> None:
    """Test successful recipe parsing returns parsed data."""
    # Arrange
    mock_parser.return_value = ParseResult(
        success=True,
        data={
            "title": "Test Recipe",
            "description": "A test recipe",
            "instructions": "Step 1. Do something.",
            "ingredients": ["1 cup flour", "2 eggs"],
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "source_url": "https://example.com/recipe",
            "image_url": "https://example.com/image.jpg",
            "tags": ["dessert", "easy"],
        },
    )

    # Act
    response = client.get("/recipes/parse?url=https://example.com/recipe")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Test Recipe"
    assert data["data"]["ingredients"] == ["1 cup flour", "2 eggs"]
    assert data["error"] is None
    assert data["duplicate_warning"] is None


def test_parse_recipe_network_error(
    client,
    mock_parser,
) -> None:
    """Test network error returns structured error response."""
    # Arrange
    mock_parser.return_value = ParseResult(
        success=False,
        error=ParseError(
            code=ParseErrorCode.NETWORK_ERROR,
            message="Failed to fetch URL: Connection refused",
            suggested_action="Check the URL and your internet connection, then try again.",
        ),
    )

    # Act
    response = client.get("/recipes/parse?url=https://example.com/recipe")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["data"] is None
    assert data["error"]["code"] == "NETWORK_ERROR"
    assert "Connection refused" in data["error"]["message"]
    assert "internet connection" in data["error"]["suggested_action"]


def test_parse_recipe_unsupported_site(
    client,
    mock_parser,
) -> None:
    """Test unsupported site returns MANUAL_ENTRY_REQUIRED error."""
    # Arrange
    mock_parser.return_value = ParseResult(
        success=False,
        error=ParseError(
            code=ParseErrorCode.MANUAL_ENTRY_REQUIRED,
            message="Could not parse recipe from this website",
            suggested_action="This website is not supported. Please enter the recipe manually.",
        ),
    )

    # Act
    response = client.get("/recipes/parse?url=https://unsupported.com/recipe")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "MANUAL_ENTRY_REQUIRED"
    assert "not supported" in data["error"]["suggested_action"].lower()


def test_parse_duplicate_warning(
    client,
    test_session: Session,
    mock_parser,
) -> None:
    """Test duplicate URL returns duplicate warning with existing recipe."""
    # Arrange - Add existing recipe to database
    existing_recipe = Recipe(
        title="Existing Recipe",
        instructions="Existing instructions",
        source_url="https://example.com/existing-recipe",
    )
    test_session.add(existing_recipe)
    test_session.commit()
    test_session.refresh(existing_recipe)

    # Mock successful parse
    mock_parser.return_value = ParseResult(
        success=True,
        data={
            "title": "Parsed Recipe",
            "instructions": "Parsed instructions",
            "source_url": "https://example.com/existing-recipe",
        },
    )

    # Act
    response = client.get(
        "/recipes/parse?url=https://example.com/existing-recipe"
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["duplicate_warning"] is not None
    assert data["duplicate_warning"]["existing_recipe"]["id"] == existing_recipe.id
    assert data["duplicate_warning"]["existing_recipe"]["title"] == "Existing Recipe"


def test_parse_no_recipe_found(
    client,
    mock_parser,
) -> None:
    """Test page with no recipe returns NO_RECIPE_FOUND error."""
    # Arrange
    mock_parser.return_value = ParseResult(
        success=False,
        error=ParseError(
            code=ParseErrorCode.NO_RECIPE_FOUND,
            message="No recipe found on this page.",
            suggested_action="Make sure the URL is a recipe page, or enter the recipe manually.",
        ),
    )

    # Act
    response = client.get("/recipes/parse?url=https://example.com/not-a-recipe")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NO_RECIPE_FOUND"
