"""Ingredient CRUD endpoints with FastAPI and SQLModel.

Provides RESTful endpoints for ingredient and ingredient group management:
- POST /{recipe_id}/groups - Create an ingredient group
- GET /{recipe_id}/groups - List ingredient groups for a recipe
- PATCH /{recipe_id}/groups/{group_id} - Update an ingredient group
- DELETE /{recipe_id}/groups/{group_id} - Delete an ingredient group
- POST /{recipe_id}/ingredients - Create an ingredient
- GET /{recipe_id}/ingredients - List all ingredients for a recipe
- PATCH /{recipe_id}/ingredients/{ingredient_id} - Update an ingredient
- DELETE /{recipe_id}/ingredients/{ingredient_id} - Delete an ingredient
- PUT /{recipe_id}/ingredients - Bulk replace all ingredients

CONTEXT.md decisions implemented:
- Default group name is "Ingredients"
- Empty groups are auto-deleted when all ingredients removed
- Deleting a group cascade-deletes all its ingredients
- Bulk operation is all-or-nothing (transaction)
- Gaps in display_order allowed
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from eat_it.database import get_session
from eat_it.models.recipe import Ingredient, IngredientGroup, Recipe
from eat_it.schemas.ingredient import (
    IngredientCreate,
    IngredientGroupCreate,
    IngredientGroupPublic,
    IngredientGroupUpdate,
    IngredientGroupWithIngredients,
    IngredientPublic,
    IngredientUpdate,
    IngredientsBulkRequest,
    IngredientsBulkResponse,
)

router = APIRouter(tags=["ingredients"])

# Default group name when auto-creating
DEFAULT_GROUP_NAME = "Ingredients"


def _get_recipe_or_404(session: Session, recipe_id: int) -> Recipe:
    """Get a recipe or raise 404 if not found."""
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


def _ensure_default_group(session: Session, recipe_id: int) -> IngredientGroup:
    """Get existing default group or create one.

    If any group exists for the recipe, returns the first one.
    Otherwise creates a new group with default name.
    """
    group = session.exec(
        select(IngredientGroup).where(IngredientGroup.recipe_id == recipe_id)
    ).first()
    if group:
        return group
    group = IngredientGroup(recipe_id=recipe_id, name=DEFAULT_GROUP_NAME)
    session.add(group)
    session.flush()
    return group


# ─── Ingredient Group Endpoints ───────────────────────────────────────────


@router.post(
    "/{recipe_id}/groups",
    response_model=IngredientGroupPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create an ingredient group",
)
def create_group(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    group: IngredientGroupCreate,
) -> IngredientGroup:
    """Create a new ingredient group for a recipe.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to add the group to.
        group: Group data for creation.

    Returns:
        The created group with generated id and timestamps.

    Raises:
        HTTPException: 404 if recipe not found.
    """
    _get_recipe_or_404(session, recipe_id)

    db_group = IngredientGroup(
        recipe_id=recipe_id,
        name=group.name,
    )
    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return db_group


@router.get(
    "/{recipe_id}/groups",
    response_model=list[IngredientGroupPublic],
    summary="List ingredient groups",
)
def list_groups(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
) -> list[IngredientGroup]:
    """List all ingredient groups for a recipe.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to list groups for.

    Returns:
        List of ingredient groups, ordered by id.

    Raises:
        HTTPException: 404 if recipe not found.
    """
    _get_recipe_or_404(session, recipe_id)

    groups = session.exec(
        select(IngredientGroup)
        .where(IngredientGroup.recipe_id == recipe_id)
        .order_by(IngredientGroup.id)
    ).all()
    return list(groups)


@router.patch(
    "/{recipe_id}/groups/{group_id}",
    response_model=IngredientGroupPublic,
    summary="Update an ingredient group",
)
def update_group(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    group_id: int,
    group: IngredientGroupUpdate,
) -> IngredientGroup:
    """Update an ingredient group (partial update).

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe the group belongs to.
        group_id: The ID of the group to update.
        group: Partial group data for update.

    Returns:
        The updated group.

    Raises:
        HTTPException: 404 if recipe or group not found.
    """
    _get_recipe_or_404(session, recipe_id)

    db_group = session.get(IngredientGroup, group_id)
    if not db_group or db_group.recipe_id != recipe_id:
        raise HTTPException(status_code=404, detail="Group not found")

    update_data = group.model_dump(exclude_unset=True)
    db_group.sqlmodel_update(update_data)
    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return db_group


@router.delete(
    "/{recipe_id}/groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an ingredient group",
)
def delete_group(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    group_id: int,
) -> None:
    """Delete an ingredient group and all its ingredients (cascade).

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe the group belongs to.
        group_id: The ID of the group to delete.

    Raises:
        HTTPException: 404 if recipe or group not found.
    """
    _get_recipe_or_404(session, recipe_id)

    db_group = session.get(IngredientGroup, group_id)
    if not db_group or db_group.recipe_id != recipe_id:
        raise HTTPException(status_code=404, detail="Group not found")

    # Cascade delete all ingredients in the group first
    session.exec(
        select(Ingredient).where(Ingredient.group_id == group_id)
    ).all()  # Load to ensure foreign key constraints handled
    ingredients = session.exec(
        select(Ingredient).where(Ingredient.group_id == group_id)
    ).all()
    for ingredient in ingredients:
        session.delete(ingredient)

    # Delete the group
    session.delete(db_group)
    session.commit()


# ─── Ingredient Endpoints ─────────────────────────────────────────────────


@router.post(
    "/{recipe_id}/ingredients",
    response_model=IngredientPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create an ingredient",
)
def create_ingredient(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    ingredient: IngredientCreate,
) -> Ingredient:
    """Create a new ingredient.

    If group_id is not provided or the group doesn't exist, auto-creates
    a default group for the recipe.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to add the ingredient to.
        ingredient: Ingredient data for creation.

    Returns:
        The created ingredient with generated id and timestamps.

    Raises:
        HTTPException: 404 if recipe not found.
    """
    _get_recipe_or_404(session, recipe_id)

    # Check if group exists, if not use/create default group
    group_id = ingredient.group_id
    group = session.get(IngredientGroup, group_id) if group_id else None
    if not group:
        group = _ensure_default_group(session, recipe_id)
        group_id = group.id

    # Calculate display_order: count of existing ingredients in group
    existing_count = len(
        session.exec(
            select(Ingredient).where(Ingredient.group_id == group_id)
        ).all()
    )

    db_ingredient = Ingredient(
        group_id=group_id,
        quantity=ingredient.quantity,
        unit=ingredient.unit,
        name=ingredient.name,
        preparation=ingredient.preparation,
        raw=ingredient.raw,
        display_order=ingredient.display_order if ingredient.display_order else existing_count,
    )
    session.add(db_ingredient)
    session.commit()
    session.refresh(db_ingredient)
    return db_ingredient


@router.get(
    "/{recipe_id}/ingredients",
    response_model=list[IngredientPublic],
    summary="List all ingredients",
)
def list_ingredients(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
) -> list[Ingredient]:
    """List all ingredients for a recipe across all groups.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to list ingredients for.

    Returns:
        List of ingredients, ordered by group_id then display_order.

    Raises:
        HTTPException: 404 if recipe not found.
    """
    _get_recipe_or_404(session, recipe_id)

    # Get all groups for this recipe
    groups = session.exec(
        select(IngredientGroup).where(IngredientGroup.recipe_id == recipe_id)
    ).all()
    group_ids = [g.id for g in groups]

    if not group_ids:
        return []

    # Get all ingredients for those groups
    ingredients = session.exec(
        select(Ingredient)
        .where(Ingredient.group_id.in_(group_ids))
        .order_by(Ingredient.group_id, Ingredient.display_order)
    ).all()
    return list(ingredients)


@router.patch(
    "/{recipe_id}/ingredients/{ingredient_id}",
    response_model=IngredientPublic,
    summary="Update an ingredient",
)
def update_ingredient(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    ingredient_id: int,
    ingredient: IngredientUpdate,
) -> Ingredient:
    """Update an ingredient (partial update).

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe the ingredient belongs to.
        ingredient_id: The ID of the ingredient to update.
        ingredient: Partial ingredient data for update.

    Returns:
        The updated ingredient.

    Raises:
        HTTPException: 404 if recipe or ingredient not found.
    """
    _get_recipe_or_404(session, recipe_id)

    db_ingredient = session.get(Ingredient, ingredient_id)
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Verify ingredient belongs to a group for this recipe
    group = session.get(IngredientGroup, db_ingredient.group_id)
    if not group or group.recipe_id != recipe_id:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    update_data = ingredient.model_dump(exclude_unset=True)
    db_ingredient.sqlmodel_update(update_data)
    session.add(db_ingredient)
    session.commit()
    session.refresh(db_ingredient)
    return db_ingredient


@router.delete(
    "/{recipe_id}/ingredients/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an ingredient",
)
def delete_ingredient(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    ingredient_id: int,
) -> None:
    """Delete an ingredient.

    If the ingredient's group becomes empty after deletion, the group
    is automatically deleted.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe the ingredient belongs to.
        ingredient_id: The ID of the ingredient to delete.

    Raises:
        HTTPException: 404 if recipe or ingredient not found.
    """
    _get_recipe_or_404(session, recipe_id)

    db_ingredient = session.get(Ingredient, ingredient_id)
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Verify ingredient belongs to a group for this recipe
    group = session.get(IngredientGroup, db_ingredient.group_id)
    if not group or group.recipe_id != recipe_id:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    group_id = db_ingredient.group_id

    # Delete the ingredient
    session.delete(db_ingredient)
    session.flush()

    # Check if group is now empty, delete if so
    remaining = session.exec(
        select(Ingredient).where(Ingredient.group_id == group_id)
    ).first()
    if not remaining:
        db_group = session.get(IngredientGroup, group_id)
        if db_group:
            session.delete(db_group)

    session.commit()


# ─── Bulk Operations ──────────────────────────────────────────────────────


@router.put(
    "/{recipe_id}/ingredients",
    response_model=IngredientsBulkResponse,
    summary="Bulk replace all ingredients",
)
def bulk_replace_ingredients(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    payload: IngredientsBulkRequest,
) -> IngredientsBulkResponse:
    """Bulk replace all groups and ingredients for a recipe.

    This is an all-or-nothing operation within a transaction.
    Existing groups/ingredients not in the payload are deleted.
    Groups/ingredients with id are updated, those without id are created.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to update.
        payload: Complete state of all groups with nested ingredients.

    Returns:
        The complete groups+ingredients structure after the operation.

    Raises:
        HTTPException: 404 if recipe not found.
    """
    _get_recipe_or_404(session, recipe_id)

    # Get all existing groups for this recipe
    existing_groups = session.exec(
        select(IngredientGroup).where(IngredientGroup.recipe_id == recipe_id)
    ).all()
    existing_group_ids = {g.id for g in existing_groups if g.id}

    # Track which groups and ingredients are in the payload
    payload_group_ids: set[int] = set()
    payload_ingredient_ids: set[int] = set()

    # Process each group in the payload
    for group_data in payload.groups:
        if group_data.id is not None:
            # Update existing group
            db_group = session.get(IngredientGroup, group_data.id)
            if db_group and db_group.recipe_id == recipe_id:
                db_group.name = group_data.name
                db_group.updated_at = datetime.utcnow()
                session.add(db_group)
                payload_group_ids.add(group_data.id)
            # If group doesn't exist or doesn't belong to recipe, skip silently
        else:
            # Create new group
            db_group = IngredientGroup(
                recipe_id=recipe_id,
                name=group_data.name,
            )
            session.add(db_group)
            session.flush()  # Get the new group ID
            payload_group_ids.add(db_group.id)

        # Get the group_id to use for ingredients
        group_id = group_data.id if group_data.id is not None else db_group.id

        # Process ingredients in this group
        for index, ingredient_data in enumerate(group_data.ingredients):
            if ingredient_data.id is not None:
                # Update existing ingredient
                db_ingredient = session.get(Ingredient, ingredient_data.id)
                if db_ingredient:
                    # Verify ingredient belongs to this recipe via its group
                    ing_group = session.get(IngredientGroup, db_ingredient.group_id)
                    if ing_group and ing_group.recipe_id == recipe_id:
                        db_ingredient.group_id = group_id
                        db_ingredient.quantity = ingredient_data.quantity
                        db_ingredient.unit = ingredient_data.unit
                        db_ingredient.name = ingredient_data.name
                        db_ingredient.preparation = ingredient_data.preparation
                        db_ingredient.raw = ingredient_data.raw
                        db_ingredient.display_order = index
                        db_ingredient.updated_at = datetime.utcnow()
                        session.add(db_ingredient)
                        payload_ingredient_ids.add(ingredient_data.id)
            else:
                # Create new ingredient
                db_ingredient = Ingredient(
                    group_id=group_id,
                    quantity=ingredient_data.quantity,
                    unit=ingredient_data.unit,
                    name=ingredient_data.name,
                    preparation=ingredient_data.preparation,
                    raw=ingredient_data.raw,
                    display_order=index,
                )
                session.add(db_ingredient)
                session.flush()  # Get the new ingredient ID
                payload_ingredient_ids.add(db_ingredient.id)

    # Delete ingredients not in payload (per-group)
    for existing_group in existing_groups:
        if existing_group.id not in payload_group_ids:
            # Delete all ingredients in this group (will cascade on group delete)
            continue
        # Delete ingredients in this group that aren't in payload
        existing_ingredients = session.exec(
            select(Ingredient).where(Ingredient.group_id == existing_group.id)
        ).all()
        for ing in existing_ingredients:
            if ing.id not in payload_ingredient_ids:
                session.delete(ing)

    # Delete groups not in payload
    for existing_group in existing_groups:
        if existing_group.id not in payload_group_ids:
            session.delete(existing_group)

    # Commit all changes
    session.commit()

    # Fetch and return the complete state
    final_groups = session.exec(
        select(IngredientGroup)
        .where(IngredientGroup.recipe_id == recipe_id)
        .order_by(IngredientGroup.id)
    ).all()

    result_groups = []
    for fg in final_groups:
        ingredients = session.exec(
            select(Ingredient)
            .where(Ingredient.group_id == fg.id)
            .order_by(Ingredient.display_order)
        ).all()
        result_groups.append(
            IngredientGroupWithIngredients(
                id=fg.id,
                recipe_id=fg.recipe_id,
                name=fg.name,
                created_at=fg.created_at,
                updated_at=fg.updated_at,
                ingredients=[IngredientPublic.model_validate(i) for i in ingredients],
            )
        )

    return IngredientsBulkResponse(groups=result_groups)
