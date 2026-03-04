"""Tests for Ingredient model with display_order field."""

import pytest
from sqlmodel import Session

from eat_it.models import Ingredient, IngredientGroup, Recipe


class TestIngredientDisplayOrder:
    """Tests for display_order field on Ingredient model."""

    def test_ingredient_has_display_order_attribute(self) -> None:
        """Ingredient model has display_order attribute."""
        ingredient = Ingredient(
            name="salt",
            raw="1 tsp salt",
            group_id=1,
        )
        assert hasattr(ingredient, "display_order")

    def test_ingredient_display_order_defaults_to_zero(self) -> None:
        """Ingredient display_order defaults to 0."""
        ingredient = Ingredient(
            name="salt",
            raw="1 tsp salt",
            group_id=1,
        )
        assert ingredient.display_order == 0

    def test_ingredient_can_be_created_with_explicit_display_order(self) -> None:
        """Ingredient can be created with explicit display_order."""
        ingredient = Ingredient(
            name="salt",
            raw="1 tsp salt",
            group_id=1,
            display_order=5,
        )
        assert ingredient.display_order == 5

    def test_ingredient_persists_display_order_to_database(
        self, test_session: Session
    ) -> None:
        """Ingredient display_order is persisted to database."""
        # Create recipe and group
        recipe = Recipe(title="Test", instructions="Test")
        test_session.add(recipe)
        test_session.commit()
        test_session.refresh(recipe)

        group = IngredientGroup(recipe_id=recipe.id, name="Main")
        test_session.add(group)
        test_session.commit()
        test_session.refresh(group)

        # Create ingredient with display_order
        ingredient = Ingredient(
            name="salt",
            raw="1 tsp salt",
            group_id=group.id,
            display_order=3,
        )
        test_session.add(ingredient)
        test_session.commit()
        test_session.refresh(ingredient)

        # Verify persistence
        assert ingredient.id is not None
        assert ingredient.display_order == 3

        # Verify retrieval
        retrieved = test_session.get(Ingredient, ingredient.id)
        assert retrieved is not None
        assert retrieved.display_order == 3
