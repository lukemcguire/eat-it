"""Shopping List CRUD endpoints with FastAPI and SQLModel.

Provides RESTful endpoints for shopping list management:
- POST /shopping-lists - Create an empty shopping list
- GET /shopping-lists - List all shopping lists
- GET /shopping-lists/{list_id} - Get a single list with items
- PATCH /shopping-lists/{list_id} - Update list name
- DELETE /shopping-lists/{list_id} - Delete a list
- POST /shopping-lists/{list_id}/items - Add item to list
- PATCH /shopping-lists/{list_id}/items/{item_id} - Update item
- DELETE /shopping-lists/{list_id}/items/{item_id} - Remove item
- POST /shopping-lists/generate - Generate list from recipes
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, col, select

from eat_it.database import get_session
from eat_it.models.recipe import Ingredient, IngredientGroup, Recipe
from eat_it.models.shopping_list import ShoppingList, ShoppingListItem
from eat_it.models.store_section import StoreSection
from eat_it.schemas.shopping_list import (
    ShoppingListCreate,
    ShoppingListGenerate,
    ShoppingListItemCreate,
    ShoppingListItemPublic,
    ShoppingListItemUpdate,
    ShoppingListPublic,
    ShoppingListsPublic,
    ShoppingListUpdate,
)
from eat_it.services.ingredient_combiner import combine_ingredients
from eat_it.services.section_categorizer import categorize_ingredient, get_or_create_section_id

router = APIRouter(tags=["shopping-lists"])


# ─── CRUD Endpoints ──────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=ShoppingListPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create an empty shopping list",
)
def create_shopping_list(
    *,
    session: Session = Depends(get_session),
    data: ShoppingListCreate,
) -> ShoppingList:
    """Create a new empty shopping list.

    Args:
        session: Database session from dependency injection.
        data: Shopping list data for creation (name only).

    Returns:
        The created shopping list with generated id and timestamps.
    """
    db_list = ShoppingList(name=data.name)
    session.add(db_list)
    session.commit()
    session.refresh(db_list)
    return db_list


@router.get(
    "/",
    response_model=ShoppingListsPublic,
    summary="List all shopping lists",
)
def list_shopping_lists(
    *,
    session: Session = Depends(get_session),
) -> ShoppingListsPublic:
    """List all shopping lists without nested items.

    Args:
        session: Database session from dependency injection.

    Returns:
        ShoppingListsPublic with all lists, ordered by created_at desc.
    """
    lists = session.exec(
        select(ShoppingList).order_by(col(ShoppingList.created_at).desc())
    ).all()

    # Return without items for performance
    return ShoppingListsPublic(
        data=[ShoppingListPublic.model_validate(lst) for lst in lists],
        count=len(lists),
    )


@router.get(
    "/{list_id}",
    response_model=ShoppingListPublic,
    summary="Get a single shopping list with items",
)
def get_shopping_list(
    *,
    session: Session = Depends(get_session),
    list_id: int,
) -> ShoppingList:
    """Get a single shopping list by ID with all items.

    Items are ordered by section sort_order then display_order.

    Args:
        session: Database session from dependency injection.
        list_id: The ID of the shopping list to retrieve.

    Returns:
        The requested shopping list with nested items.

    Raises:
        HTTPException: 404 if list not found.
    """
    db_list = session.get(ShoppingList, list_id)
    if not db_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    # Fetch items ordered by section sort_order then display_order
    items = session.exec(
        select(ShoppingListItem)
        .where(ShoppingListItem.shopping_list_id == list_id)
        .join(StoreSection, isouter=True)
        .order_by(
            col(StoreSection.sort_order).asc(),
            col(ShoppingListItem.display_order).asc(),
        )
    ).all()

    # Build response with ordered items
    return ShoppingListPublic(
        id=db_list.id,
        name=db_list.name,
        share_token=db_list.share_token,
        expires_at=db_list.expires_at,
        items=[ShoppingListItemPublic.model_validate(item) for item in items],
        created_at=db_list.created_at,
        updated_at=db_list.updated_at,
    )


@router.patch(
    "/{list_id}",
    response_model=ShoppingListPublic,
    summary="Update shopping list name",
)
def update_shopping_list(
    *,
    session: Session = Depends(get_session),
    list_id: int,
    data: ShoppingListUpdate,
) -> ShoppingList:
    """Update a shopping list with partial data.

    Only provided fields will be updated.

    Args:
        session: Database session from dependency injection.
        list_id: The ID of the shopping list to update.
        data: Partial shopping list data for update.

    Returns:
        The updated shopping list.

    Raises:
        HTTPException: 404 if list not found.
    """
    db_list = session.get(ShoppingList, list_id)
    if not db_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    db_list.sqlmodel_update(update_data)
    session.add(db_list)
    session.commit()
    session.refresh(db_list)
    return db_list


@router.delete(
    "/{list_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a shopping list",
)
def delete_shopping_list(
    *,
    session: Session = Depends(get_session),
    list_id: int,
) -> None:
    """Delete a shopping list by ID.

    Cascades to delete all items in the list.

    Args:
        session: Database session from dependency injection.
        list_id: The ID of the shopping list to delete.

    Raises:
        HTTPException: 404 if list not found.
    """
    db_list = session.get(ShoppingList, list_id)
    if not db_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )
    session.delete(db_list)
    session.commit()


# ─── Item Endpoints ──────────────────────────────────────────────────────


@router.post(
    "/{list_id}/items",
    response_model=ShoppingListItemPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to shopping list",
)
def add_shopping_list_item(
    *,
    session: Session = Depends(get_session),
    list_id: int,
    data: ShoppingListItemCreate,
) -> ShoppingListItem:
    """Add an item to a shopping list.

    Auto-categorizes to a store section if section_id not provided.

    Args:
        session: Database session from dependency injection.
        list_id: The ID of the shopping list.
        data: Item data for creation.

    Returns:
        The created shopping list item.

    Raises:
        HTTPException: 404 if list not found.
    """
    db_list = session.get(ShoppingList, list_id)
    if not db_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    # Auto-categorize if section_id not provided
    section_id = data.section_id
    if section_id is None:
        section_name = categorize_ingredient(data.name)
        section_id = get_or_create_section_id(session, section_name)

    db_item = ShoppingListItem(
        shopping_list_id=list_id,
        name=data.name,
        quantity=data.quantity,
        unit=data.unit,
        section_id=section_id,
        display_order=data.display_order,
        checked=data.checked,
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.patch(
    "/{list_id}/items/{item_id}",
    response_model=ShoppingListItemPublic,
    summary="Update shopping list item",
)
def update_shopping_list_item(
    *,
    session: Session = Depends(get_session),
    list_id: int,
    item_id: int,
    data: ShoppingListItemUpdate,
) -> ShoppingListItem:
    """Update a shopping list item with partial data.

    Only provided fields will be updated.

    Args:
        session: Database session from dependency injection.
        list_id: The ID of the shopping list.
        item_id: The ID of the item to update.
        data: Partial item data for update.

    Returns:
        The updated shopping list item.

    Raises:
        HTTPException: 404 if list or item not found.
    """
    db_list = session.get(ShoppingList, list_id)
    if not db_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    db_item = session.get(ShoppingListItem, item_id)
    if not db_item or db_item.shopping_list_id != list_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in this shopping list",
        )

    update_data = data.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete(
    "/{list_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from shopping list",
)
def delete_shopping_list_item(
    *,
    session: Session = Depends(get_session),
    list_id: int,
    item_id: int,
) -> None:
    """Remove an item from a shopping list.

    Args:
        session: Database session from dependency injection.
        list_id: The ID of the shopping list.
        item_id: The ID of the item to delete.

    Raises:
        HTTPException: 404 if list or item not found.
    """
    db_list = session.get(ShoppingList, list_id)
    if not db_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    db_item = session.get(ShoppingListItem, item_id)
    if not db_item or db_item.shopping_list_id != list_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in this shopping list",
        )

    session.delete(db_item)
    session.commit()


# ─── Generate Endpoint ───────────────────────────────────────────────────


@router.post(
    "/generate",
    response_model=ShoppingListPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Generate shopping list from recipes",
)
def generate_shopping_list(
    *,
    session: Session = Depends(get_session),
    data: ShoppingListGenerate,
) -> ShoppingList:
    """Generate a shopping list from selected recipes.

    Combines ingredients from all recipes, auto-categorizes to sections,
    and creates the shopping list with items.

    Args:
        session: Database session from dependency injection.
        data: Generate request with list name and recipe IDs.

    Returns:
        The created shopping list with all items.

    Note:
        Invalid recipe IDs are silently skipped.
    """
    # Collect all ingredient raw strings from recipes
    all_ingredients: list[str] = []
    for recipe_id in data.recipe_ids:
        recipe = session.get(Recipe, recipe_id)
        if not recipe:
            continue  # Skip invalid recipe IDs

        groups = session.exec(
            select(IngredientGroup).where(IngredientGroup.recipe_id == recipe_id)
        ).all()

        for group in groups:
            ingredients = session.exec(
                select(Ingredient).where(Ingredient.group_id == group.id)
            ).all()
            all_ingredients.extend([ing.raw for ing in ingredients])

    # Combine ingredients
    combined = combine_ingredients(all_ingredients)

    # Create list
    db_list = ShoppingList(name=data.name)
    session.add(db_list)
    session.commit()
    session.refresh(db_list)

    # Create items with auto-categorization
    for item in combined:
        section_name = categorize_ingredient(item.name)
        section_id = get_or_create_section_id(session, section_name)
        db_item = ShoppingListItem(
            shopping_list_id=db_list.id,
            name=item.name,
            quantity=item.quantity,
            unit=item.unit,
            section_id=section_id,
        )
        session.add(db_item)

    session.commit()
    session.refresh(db_list)

    # Fetch items ordered by section sort_order then display_order
    items = session.exec(
        select(ShoppingListItem)
        .where(ShoppingListItem.shopping_list_id == db_list.id)
        .join(StoreSection, isouter=True)
        .order_by(
            col(StoreSection.sort_order).asc(),
            col(ShoppingListItem.display_order).asc(),
        )
    ).all()

    # Build response with ordered items
    return ShoppingListPublic(
        id=db_list.id,
        name=db_list.name,
        share_token=db_list.share_token,
        expires_at=db_list.expires_at,
        items=[ShoppingListItemPublic.model_validate(item) for item in items],
        created_at=db_list.created_at,
        updated_at=db_list.updated_at,
    )
