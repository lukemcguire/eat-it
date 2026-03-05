"""Tests for ingredient CRUD endpoints including groups and bulk operations."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from eat_it.models.recipe import Ingredient, IngredientGroup, Recipe


def _create_recipe(session: Session) -> Recipe:
    """Create a test recipe and return it."""
    recipe = Recipe(title="Test Recipe", instructions="Test instructions")
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


def _create_group(session: Session, recipe_id: int, name: str = "Test Group") -> IngredientGroup:
    """Create a test ingredient group and return it."""
    group = IngredientGroup(recipe_id=recipe_id, name=name)
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def _create_ingredient(
    session: Session,
    group_id: int,
    name: str = "Test Ingredient",
    raw: str = "1 cup test ingredient",
) -> Ingredient:
    """Create a test ingredient and return it."""
    ingredient = Ingredient(group_id=group_id, name=name, raw=raw)
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)
    return ingredient


class TestCreateGroup:
    """Tests for POST /recipes/{recipe_id}/groups endpoint."""

    def test_create_group(self, client: TestClient, test_session: Session) -> None:
        """POST /recipes/{id}/groups returns 201 with group data."""
        recipe = _create_recipe(test_session)

        response = client.post(f"/recipes/{recipe.id}/groups", json={"name": "Sauce"})

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Sauce"
        assert data["recipe_id"] == recipe.id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_group_recipe_not_found(self, client: TestClient) -> None:
        """POST /recipes/999/groups returns 404."""
        response = client.post("/recipes/999/groups", json={"name": "Test"})

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"


class TestListGroups:
    """Tests for GET /recipes/{recipe_id}/groups endpoint."""

    def test_list_groups_empty(self, client: TestClient, test_session: Session) -> None:
        """GET /recipes/{id}/groups returns empty list when no groups."""
        recipe = _create_recipe(test_session)

        response = client.get(f"/recipes/{recipe.id}/groups")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_groups(
        self, client: TestClient, test_session: Session
    ) -> None:
        """GET /recipes/{id}/groups returns all groups for recipe."""
        recipe = _create_recipe(test_session)
        _create_group(test_session, recipe.id, "Group 1")
        _create_group(test_session, recipe.id, "Group 2")

        response = client.get(f"/recipes/{recipe.id}/groups")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [g["name"] for g in data]
        assert "Group 1" in names
        assert "Group 2" in names

    def test_list_groups_recipe_not_found(self, client: TestClient) -> None:
        """GET /recipes/999/groups returns 404."""
        response = client.get("/recipes/999/groups")

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"


class TestUpdateGroup:
    """Tests for PATCH /recipes/{recipe_id}/groups/{group_id} endpoint."""

    def test_update_group(
        self, client: TestClient, test_session: Session
    ) -> None:
        """PATCH /recipes/{id}/groups/{group_id} updates name."""
        recipe = _create_recipe(test_session)
        group = _create_group(test_session, recipe.id, "Original Name")

        response = client.patch(
            f"/recipes/{recipe.id}/groups/{group.id}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_group_not_found(
        self, client: TestClient, test_session: Session
    ) -> None:
        """PATCH /recipes/{id}/groups/999 returns 404."""
        recipe = _create_recipe(test_session)

        response = client.patch(
            f"/recipes/{recipe.id}/groups/999",
            json={"name": "New Name"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Group not found"

    def test_update_group_recipe_not_found(self, client: TestClient) -> None:
        """PATCH /recipes/999/groups/1 returns 404."""
        response = client.patch("/recipes/999/groups/1", json={"name": "New Name"})

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"


class TestDeleteGroup:
    """Tests for DELETE /recipes/{recipe_id}/groups/{group_id} endpoint."""

    def test_delete_group(
        self, client: TestClient, test_session: Session
    ) -> None:
        """DELETE /recipes/{id}/groups/{group_id} returns 204."""
        recipe = _create_recipe(test_session)
        group = _create_group(test_session, recipe.id)

        response = client.delete(f"/recipes/{recipe.id}/groups/{group.id}")

        assert response.status_code == 204
        assert response.content == b""

    def test_delete_group_removes_ingredients(
        self, client: TestClient, test_session: Session
    ) -> None:
        """DELETE group removes its ingredients."""
        recipe = _create_recipe(test_session)
        group = _create_group(test_session, recipe.id)
        ingredient = _create_ingredient(test_session, group.id)

        # Delete the group
        response = client.delete(f"/recipes/{recipe.id}/groups/{group.id}")
        assert response.status_code == 204

        # Verify ingredient is gone
        response = client.get(f"/recipes/{recipe.id}/ingredients")
        assert response.status_code == 200
        assert response.json() == []

    def test_delete_group_not_found(
        self, client: TestClient, test_session: Session
    ) -> None:
        """DELETE /recipes/{id}/groups/999 returns 404."""
        recipe = _create_recipe(test_session)

        response = client.delete(f"/recipes/{recipe.id}/groups/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Group not found"


class TestCreateIngredient:
    """Tests for POST /recipes/{recipe_id}/ingredients endpoint."""

    def test_create_ingredient(
        self, client: TestClient, test_session: Session
    ) -> None:
        """POST /recipes/{id}/ingredients returns 201 with ingredient data."""
        recipe = _create_recipe(test_session)
        group = _create_group(test_session, recipe.id)

        ingredient_data = {
            "group_id": group.id,
            "quantity": 1.5,
            "unit": "cups",
            "name": "Flour",
            "preparation": "sifted",
            "raw": "1.5 cups flour, sifted",
            "display_order": 0,
        }

        response = client.post(
            f"/recipes/{recipe.id}/ingredients", json=ingredient_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["group_id"] == group.id
        assert data["quantity"] == 1.5
        assert data["unit"] == "cups"
        assert data["name"] == "Flour"
        assert data["preparation"] == "sifted"
        assert data["raw"] == "1.5 cups flour, sifted"
        assert data["display_order"] == 0

    def test_create_ingredient_auto_default_group(
        self, client: TestClient, test_session: Session
    ) -> None:
        """POST ingredient without valid group_id auto-creates default group."""
        recipe = _create_recipe(test_session)

        ingredient_data = {
            "group_id": 999,  # Non-existent group
            "name": "Salt",
            "raw": "Salt to taste",
        }

        response = client.post(
            f"/recipes/{recipe.id}/ingredients", json=ingredient_data
        )

        assert response.status_code == 201
        data = response.json()
        # Should have created a default group
        assert data["group_id"] is not None

        # Verify the group was created with default name
        groups_response = client.get(f"/recipes/{recipe.id}/groups")
        groups = groups_response.json()
        assert len(groups) == 1
        assert groups[0]["name"] == "Ingredients"

    def test_create_ingredient_missing_group_id(
        self, client: TestClient, test_session: Session
    ) -> None:
        """POST ingredient without group_id auto-creates default group."""
        recipe = _create_recipe(test_session)

        ingredient_data = {
            # No group_id provided
            "name": "Pepper",
            "raw": "Pepper to taste",
        }

        response = client.post(
            f"/recipes/{recipe.id}/ingredients", json=ingredient_data
        )

        assert response.status_code == 201
        data = response.json()
        # Should have created a default group
        assert data["group_id"] is not None

        # Verify the group was created with default name
        groups_response = client.get(f"/recipes/{recipe.id}/groups")
        groups = groups_response.json()
        assert len(groups) == 1
        assert groups[0]["name"] == "Ingredients"

    def test_create_ingredient_recipe_not_found(self, client: TestClient) -> None:
        """POST /recipes/999/ingredients returns 404."""
        response = client.post(
            "/recipes/999/ingredients",
            json={"group_id": 1, "name": "Test", "raw": "Test"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"


class TestListIngredients:
    """Tests for GET /recipes/{recipe_id}/ingredients endpoint."""

    def test_list_ingredients_empty(
        self, client: TestClient, test_session: Session
    ) -> None:
        """GET /recipes/{id}/ingredients returns empty list when no ingredients."""
        recipe = _create_recipe(test_session)

        response = client.get(f"/recipes/{recipe.id}/ingredients")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_ingredients(
        self, client: TestClient, test_session: Session
    ) -> None:
        """GET /recipes/{id}/ingredients returns all ingredients ordered by group_id,
        display_order."""
        recipe = _create_recipe(test_session)
        group1 = _create_group(test_session, recipe.id, "Group 1")
        group2 = _create_group(test_session, recipe.id, "Group 2")

        # Create ingredients with specific display orders
        ing1 = _create_ingredient(test_session, group1.id, "First", "raw1")
        ing1.display_order = 0
        test_session.add(ing1)

        ing2 = _create_ingredient(test_session, group1.id, "Second", "raw2")
        ing2.display_order = 1
        test_session.add(ing2)

        ing3 = _create_ingredient(test_session, group2.id, "Third", "raw3")
        ing3.display_order = 0
        test_session.add(ing3)

        test_session.commit()

        response = client.get(f"/recipes/{recipe.id}/ingredients")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Verify ordering: group1 items first (by display_order), then group2
        assert data[0]["name"] == "First"
        assert data[1]["name"] == "Second"
        assert data[2]["name"] == "Third"

    def test_list_ingredients_recipe_not_found(self, client: TestClient) -> None:
        """GET /recipes/999/ingredients returns 404."""
        response = client.get("/recipes/999/ingredients")

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"


class TestUpdateIngredient:
    """Tests for PATCH /recipes/{recipe_id}/ingredients/{ingredient_id} endpoint."""

    def test_update_ingredient(
        self, client: TestClient, test_session: Session
    ) -> None:
        """PATCH /recipes/{id}/ingredients/{ingredient_id} updates fields."""
        recipe = _create_recipe(test_session)
        group = _create_group(test_session, recipe.id)
        ingredient = _create_ingredient(
            test_session, group.id, "Original", "1 cup original"
        )

        response = client.patch(
            f"/recipes/{recipe.id}/ingredients/{ingredient.id}",
            json={"name": "Updated", "quantity": 2.0},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["quantity"] == 2.0

    def test_update_ingredient_not_found(
        self, client: TestClient, test_session: Session
    ) -> None:
        """PATCH /recipes/{id}/ingredients/999 returns 404."""
        recipe = _create_recipe(test_session)

        response = client.patch(
            f"/recipes/{recipe.id}/ingredients/999",
            json={"name": "Updated"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Ingredient not found"

    def test_update_ingredient_recipe_not_found(self, client: TestClient) -> None:
        """PATCH /recipes/999/ingredients/1 returns 404."""
        response = client.patch(
            "/recipes/999/ingredients/1",
            json={"name": "Updated"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"


class TestDeleteIngredient:
    """Tests for DELETE /recipes/{recipe_id}/ingredients/{ingredient_id} endpoint."""

    def test_delete_ingredient(
        self, client: TestClient, test_session: Session
    ) -> None:
        """DELETE /recipes/{id}/ingredients/{ingredient_id} returns 204."""
        recipe = _create_recipe(test_session)
        group = _create_group(test_session, recipe.id)
        ingredient = _create_ingredient(test_session, group.id)

        response = client.delete(
            f"/recipes/{recipe.id}/ingredients/{ingredient.id}"
        )

        assert response.status_code == 204
        assert response.content == b""

    def test_delete_ingredient_removes_empty_group(
        self, client: TestClient, test_session: Session
    ) -> None:
        """DELETE last ingredient removes empty group."""
        recipe = _create_recipe(test_session)
        group = _create_group(test_session, recipe.id)
        ingredient = _create_ingredient(test_session, group.id)

        # Delete the only ingredient
        response = client.delete(
            f"/recipes/{recipe.id}/ingredients/{ingredient.id}"
        )
        assert response.status_code == 204

        # Verify group was removed
        groups_response = client.get(f"/recipes/{recipe.id}/groups")
        assert groups_response.json() == []

    def test_delete_ingredient_not_found(
        self, client: TestClient, test_session: Session
    ) -> None:
        """DELETE /recipes/{id}/ingredients/999 returns 404."""
        recipe = _create_recipe(test_session)

        response = client.delete(f"/recipes/{recipe.id}/ingredients/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Ingredient not found"


class TestBulkReplace:
    """Tests for PUT /recipes/{recipe_id}/ingredients bulk replacement endpoint."""

    def test_bulk_replace_creates_all(
        self, client: TestClient, test_session: Session
    ) -> None:
        """PUT bulk creates new groups and ingredients."""
        recipe = _create_recipe(test_session)

        payload = {
            "groups": [
                {
                    "name": "Dry Ingredients",
                    "ingredients": [
                        {
                            "name": "Flour",
                            "raw": "2 cups flour",
                            "quantity": 2.0,
                            "unit": "cups",
                        },
                        {
                            "name": "Sugar",
                            "raw": "1 cup sugar",
                            "quantity": 1.0,
                            "unit": "cup",
                        },
                    ],
                },
                {
                    "name": "Wet Ingredients",
                    "ingredients": [
                        {
                            "name": "Eggs",
                            "raw": "2 eggs",
                            "quantity": 2.0,
                            "unit": None,
                        },
                    ],
                },
            ]
        }

        response = client.put(f"/recipes/{recipe.id}/ingredients", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert len(data["groups"]) == 2
        assert len(data["groups"][0]["ingredients"]) == 2
        assert len(data["groups"][1]["ingredients"]) == 1

    def test_bulk_replace_updates_existing(
        self, client: TestClient, test_session: Session
    ) -> None:
        """PUT bulk updates existing items."""
        recipe = _create_recipe(test_session)
        group = _create_group(test_session, recipe.id, "Original Group")
        ingredient = _create_ingredient(
            test_session, group.id, "Original", "1 cup original"
        )

        payload = {
            "groups": [
                {
                    "id": group.id,
                    "name": "Updated Group",
                    "ingredients": [
                        {
                            "id": ingredient.id,
                            "name": "Updated Ingredient",
                            "raw": "2 cups updated",
                            "quantity": 2.0,
                            "unit": "cups",
                        }
                    ],
                }
            ]
        }

        response = client.put(f"/recipes/{recipe.id}/ingredients", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["groups"][0]["name"] == "Updated Group"
        assert data["groups"][0]["ingredients"][0]["name"] == "Updated Ingredient"

    def test_bulk_replace_deletes_missing(
        self, client: TestClient, test_session: Session
    ) -> None:
        """PUT bulk deletes groups not in payload."""
        recipe = _create_recipe(test_session)
        group1 = _create_group(test_session, recipe.id, "Keep This")
        group2 = _create_group(test_session, recipe.id, "Delete This")

        payload = {
            "groups": [
                {
                    "id": group1.id,
                    "name": "Keep This",
                    "ingredients": [],
                }
            ]
        }

        response = client.put(f"/recipes/{recipe.id}/ingredients", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert len(data["groups"]) == 1
        assert data["groups"][0]["name"] == "Keep This"

    def test_bulk_replace_display_order(
        self, client: TestClient, test_session: Session
    ) -> None:
        """PUT bulk sets display_order from array position."""
        recipe = _create_recipe(test_session)
        group = _create_group(test_session, recipe.id)

        payload = {
            "groups": [
                {
                    "id": group.id,
                    "name": "Test Group",
                    "ingredients": [
                        {"name": "First", "raw": "first"},
                        {"name": "Second", "raw": "second"},
                        {"name": "Third", "raw": "third"},
                    ],
                }
            ]
        }

        response = client.put(f"/recipes/{recipe.id}/ingredients", json=payload)

        assert response.status_code == 200
        data = response.json()
        ingredients = data["groups"][0]["ingredients"]

        # Verify display_order matches array position (0, 1, 2)
        assert ingredients[0]["display_order"] == 0
        assert ingredients[1]["display_order"] == 1
        assert ingredients[2]["display_order"] == 2

    def test_bulk_replace_recipe_not_found(self, client: TestClient) -> None:
        """PUT /recipes/999/ingredients returns 404."""
        response = client.put(
            "/recipes/999/ingredients",
            json={"groups": []},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"
