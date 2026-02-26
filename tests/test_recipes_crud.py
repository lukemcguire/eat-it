"""Tests for recipe CRUD endpoints including annotation endpoints."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from eat_it.models.recipe import Recipe


class TestCreateRecipe:
    """Tests for POST /recipes endpoint."""

    def test_create_recipe(self, client: TestClient) -> None:
        """POST /recipes returns 201 with recipe data."""
        recipe_data = {
            "title": "Test Recipe",
            "instructions": "Mix and cook.",
        }

        response = client.post("/recipes/", json=recipe_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Recipe"
        assert data["instructions"] == "Mix and cook."
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_recipe_with_all_fields(self, client: TestClient) -> None:
        """POST /recipes accepts all optional fields."""
        recipe_data = {
            "title": "Full Recipe",
            "description": "A complete recipe",
            "instructions": "Step by step",
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "source_url": "https://example.com/recipe",
            "image_url": "https://example.com/image.jpg",
            "tags": ["dinner", "quick"],
        }

        response = client.post("/recipes/", json=recipe_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Full Recipe"
        assert data["description"] == "A complete recipe"
        assert data["prep_time"] == 15
        assert data["cook_time"] == 30
        assert data["servings"] == 4
        assert data["source_url"] == "https://example.com/recipe"
        assert data["image_url"] == "https://example.com/image.jpg"
        assert data["tags"] == ["dinner", "quick"]

    def test_create_recipe_validation_error(self, client: TestClient) -> None:
        """POST /recipes returns 422 for invalid data."""
        recipe_data = {
            "title": "",  # Empty title should fail
            "instructions": "Some instructions",
        }

        response = client.post("/recipes/", json=recipe_data)

        assert response.status_code == 422


class TestListRecipes:
    """Tests for GET /recipes endpoint."""

    def test_list_recipes_empty(self, client: TestClient) -> None:
        """GET /recipes returns empty list when no recipes."""
        response = client.get("/recipes/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_recipes(self, client: TestClient, test_session: Session) -> None:
        """GET /recipes returns list with pagination."""
        # Create test recipes
        recipe1 = Recipe(
            title="Recipe 1",
            instructions="Instructions 1",
        )
        recipe2 = Recipe(
            title="Recipe 2",
            instructions="Instructions 2",
        )
        test_session.add(recipe1)
        test_session.add(recipe2)
        test_session.commit()

        response = client.get("/recipes/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        titles = [r["title"] for r in data]
        assert "Recipe 1" in titles
        assert "Recipe 2" in titles

    def test_list_recipes_pagination(
        self,
        client: TestClient,
        test_session: Session,
    ) -> None:
        """GET /recipes respects offset and limit params."""
        # Create multiple recipes
        for i in range(5):
            recipe = Recipe(
                title=f"Recipe {i}",
                instructions=f"Instructions {i}",
            )
            test_session.add(recipe)
        test_session.commit()

        # Test offset
        response = client.get("/recipes/?offset=2")
        assert len(response.json()) == 3

        # Test limit
        response = client.get("/recipes/?limit=2")
        assert len(response.json()) == 2

        # Test both
        response = client.get("/recipes/?offset=1&limit=2")
        assert len(response.json()) == 2

    def test_list_recipes_with_search(
        self,
        client: TestClient,
        test_session: Session,
    ) -> None:
        """GET /recipes?q= filters results by title/description."""
        # Create recipes with different content
        recipe1 = Recipe(
            title="Pasta Carbonara",
            description="Classic Italian pasta",
            instructions="Cook pasta",
        )
        recipe2 = Recipe(
            title="Chicken Curry",
            description="Spicy Indian curry",
            instructions="Cook chicken",
        )
        recipe3 = Recipe(
            title="Garden Salad",
            description="Fresh and healthy",
            instructions="Mix vegetables",
        )
        test_session.add(recipe1)
        test_session.add(recipe2)
        test_session.add(recipe3)
        test_session.commit()

        # Search for "pasta"
        response = client.get("/recipes/?q=pasta")
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Pasta Carbonara"

        # Search for "curry" (matches description)
        response = client.get("/recipes/?q=curry")
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Chicken Curry"

        # Search for non-existent term
        response = client.get("/recipes/?q=tacos")
        assert response.json() == []


class TestGetRecipe:
    """Tests for GET /recipes/{recipe_id} endpoint."""

    def test_get_recipe(
        self,
        client: TestClient,
        test_session: Session,
    ) -> None:
        """GET /recipes/{id} returns single recipe."""
        recipe = Recipe(
            title="Test Recipe",
            instructions="Test instructions",
        )
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)

        response = client.get(f"/recipes/{recipe.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recipe.id
        assert data["title"] == "Test Recipe"
        assert data["instructions"] == "Test instructions"

    def test_get_recipe_not_found(self, client: TestClient) -> None:
        """GET /recipes/999 returns 404."""
        response = client.get("/recipes/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"


class TestUpdateRecipe:
    """Tests for PATCH /recipes/{recipe_id} endpoint."""

    def test_update_recipe(
        self,
        client: TestClient,
        test_session: Session,
    ) -> None:
        """PATCH /recipes/{id} updates fields."""
        recipe = Recipe(
            title="Original Title",
            instructions="Original instructions",
            servings=2,
        )
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)

        update_data = {
            "title": "Updated Title",
            "servings": 4,
        }

        response = client.patch(f"/recipes/{recipe.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["servings"] == 4
        # Instructions should remain unchanged
        assert data["instructions"] == "Original instructions"

    def test_update_recipe_not_found(self, client: TestClient) -> None:
        """PATCH /recipes/999 returns 404."""
        update_data = {"title": "New Title"}

        response = client.patch("/recipes/999", json=update_data)

        assert response.status_code == 404

    def test_update_recipe_partial(
        self,
        client: TestClient,
        test_session: Session,
    ) -> None:
        """PATCH only updates provided fields (partial update)."""
        recipe = Recipe(
            title="Test Recipe",
            description="Test description",
            instructions="Test instructions",
            prep_time=10,
            cook_time=20,
        )
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)

        # Only update prep_time
        update_data = {"prep_time": 15}

        response = client.patch(f"/recipes/{recipe.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["prep_time"] == 15
        # Other fields unchanged
        assert data["title"] == "Test Recipe"
        assert data["description"] == "Test description"
        assert data["cook_time"] == 20


class TestDeleteRecipe:
    """Tests for DELETE /recipes/{recipe_id} endpoint."""

    def test_delete_recipe(
        self,
        client: TestClient,
        test_session: Session,
    ) -> None:
        """DELETE /recipes/{id} returns 204."""
        recipe = Recipe(
            title="To Delete",
            instructions="Will be deleted",
        )
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)
        recipe_id = recipe.id

        response = client.delete(f"/recipes/{recipe_id}")

        assert response.status_code == 204
        assert response.content == b""

        # Verify deleted
        response = client.get(f"/recipes/{recipe_id}")
        assert response.status_code == 404

    def test_delete_recipe_not_found(self, client: TestClient) -> None:
        """DELETE /recipes/999 returns 404."""
        response = client.delete("/recipes/999")

        assert response.status_code == 404


class TestRecipeRatingEndpoint:
    """Tests for PATCH /recipes/{id}/rating endpoint."""

    def test_update_recipe_rating(self, client: TestClient, test_session) -> None:
        """PATCH /recipes/{id}/rating sets rating."""
        # Create a recipe first
        recipe = Recipe(
            title="Test Recipe",
            instructions="Test instructions",
        )
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)
        recipe_id = recipe.id

        # Update the rating
        response = client.patch(
            f"/recipes/{recipe_id}/rating",
            json={"rating": 4},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rating"] == 4

    def test_update_recipe_rating_clear(
        self, client: TestClient, test_session
    ) -> None:
        """PATCH with null clears rating."""
        # Create a recipe with a rating
        recipe = Recipe(
            title="Test Recipe",
            instructions="Test instructions",
            rating=3,
        )
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)
        recipe_id = recipe.id

        # Clear the rating
        response = client.patch(
            f"/recipes/{recipe_id}/rating",
            json={"rating": None},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rating"] is None

    def test_update_recipe_rating_validation(
        self, client: TestClient, test_session
    ) -> None:
        """Rating outside 1-5 returns 422."""
        # Create a recipe first
        recipe = Recipe(
            title="Test Recipe",
            instructions="Test instructions",
        )
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)
        recipe_id = recipe.id

        # Try to set an invalid rating (too high)
        response = client.patch(
            f"/recipes/{recipe_id}/rating",
            json={"rating": 6},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Try to set an invalid rating (too low)
        response = client.patch(
            f"/recipes/{recipe_id}/rating",
            json={"rating": 0},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_recipe_rating_not_found(self, client: TestClient) -> None:
        """Non-existent recipe returns 404."""
        response = client.patch(
            "/recipes/99999/rating",
            json={"rating": 3},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRecipeNotesEndpoint:
    """Tests for PATCH /recipes/{id}/notes endpoint."""

    def test_update_recipe_notes(self, client: TestClient, test_session) -> None:
        """PATCH /recipes/{id}/notes sets notes."""
        # Create a recipe first
        recipe = Recipe(
            title="Test Recipe",
            instructions="Test instructions",
        )
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)
        recipe_id = recipe.id

        # Update the notes
        response = client.patch(
            f"/recipes/{recipe_id}/notes",
            json={"notes": "This is a great recipe!"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["notes"] == "This is a great recipe!"

    def test_update_recipe_notes_clear(self, client: TestClient, test_session) -> None:
        """PATCH with null clears notes."""
        # Create a recipe with notes
        recipe = Recipe(
            title="Test Recipe",
            instructions="Test instructions",
            notes="Original notes",
        )
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)
        recipe_id = recipe.id

        # Clear the notes
        response = client.patch(
            f"/recipes/{recipe_id}/notes",
            json={"notes": None},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["notes"] is None

    def test_update_recipe_notes_not_found(self, client: TestClient) -> None:
        """Non-existent recipe returns 404."""
        response = client.patch(
            "/recipes/99999/notes",
            json={"notes": "Some notes"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestExportRecipes:
    """Tests for GET /recipes/export endpoint."""

    def test_export_recipes_json(
        self, client: TestClient, test_session: Session
    ) -> None:
        """GET /recipes/export?format=json returns JSON array."""
        # Create a recipe first
        recipe = Recipe(
            title="Test Recipe",
            instructions="Test instructions",
        )
        test_session.add(recipe)
        test_session.commit()

        response = client.get("/recipes/export?format=json")

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/json"
        assert "attachment" in response.headers.get("content-disposition", "")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Verify recipe fields are present
        first_recipe = data[0]
        assert "title" in first_recipe
        assert "instructions" in first_recipe

    def test_export_recipes_csv(
        self, client: TestClient, test_session: Session
    ) -> None:
        """GET /recipes/export?format=csv returns CSV with header."""
        # Create a recipe first
        recipe = Recipe(
            title="CSV Test",
            instructions="Line 1\nLine 2",  # Test newline escaping
            tags=["dinner", "quick"],
        )
        test_session.add(recipe)
        test_session.commit()

        response = client.get("/recipes/export?format=csv")

        assert response.status_code == status.HTTP_200_OK
        assert "text/csv" in response.headers["content-type"]
        assert "attachment" in response.headers.get("content-disposition", "")
        content = response.text
        lines = content.strip().split("\n")
        # First line is header
        assert "id,title,description" in lines[0]
        # Data row should have escaped newlines
        assert len(lines) >= 2

    def test_export_recipes_content_disposition(
        self, client: TestClient, test_session: Session
    ) -> None:
        """Response has Content-Disposition attachment header."""
        recipe = Recipe(title="Test", instructions="Test")
        test_session.add(recipe)
        test_session.commit()

        # Test JSON
        response = client.get("/recipes/export?format=json")
        disposition = response.headers.get("content-disposition", "")
        assert "attachment" in disposition
        assert "recipes.json" in disposition

        # Test CSV
        response = client.get("/recipes/export?format=csv")
        disposition = response.headers.get("content-disposition", "")
        assert "attachment" in disposition
        assert "recipes.csv" in disposition

    def test_export_recipes_invalid_format(self, client: TestClient) -> None:
        """Invalid format returns 422."""
        response = client.get("/recipes/export?format=xml")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_export_recipes_empty(self, client: TestClient) -> None:
        """Empty collection returns valid empty export."""
        # Test empty JSON
        response = client.get("/recipes/export?format=json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

        # Test empty CSV
        response = client.get("/recipes/export?format=csv")
        assert response.status_code == status.HTTP_200_OK
        # CSV should still have header row
        content = response.text.strip()
        assert "id,title" in content
