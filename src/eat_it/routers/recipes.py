"""Recipe CRUD endpoints with FastAPI and SQLModel.

Provides RESTful endpoints for recipe management:
- POST /recipes - Create a new recipe
- GET /recipes - List recipes with pagination and search
- GET /recipes/{recipe_id} - Get a single recipe
- PATCH /recipes/{recipe_id} - Update a recipe (partial)
- DELETE /recipes/{recipe_id} - Delete a recipe

Note: Rating and notes updates are handled by separate endpoints
(PATCH /recipes/{id}/rating, PATCH /recipes/{id}/notes) per CONTEXT.md
decision "Separate annotation endpoints".
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, col, select

from eat_it.database import get_session
from eat_it.models.recipe import Recipe
from eat_it.schemas.recipe import RecipeCreate, RecipePublic, RecipeUpdate

router = APIRouter(tags=["recipes"])


@router.post(
    "/",
    response_model=RecipePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recipe",
)
def create_recipe(
    *,
    session: Session = Depends(get_session),
    recipe: RecipeCreate,
) -> Recipe:
    """Create a new recipe manually or from parsed URL data.

    Args:
        session: Database session from dependency injection.
        recipe: Recipe data for creation.

    Returns:
        The created recipe with generated id and timestamps.

    """
    db_recipe = Recipe.model_validate(recipe)
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe


@router.get(
    "/",
    response_model=list[RecipePublic],
    summary="List recipes with pagination",
)
def list_recipes(
    *,
    session: Session = Depends(get_session),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    q: Optional[str] = Query(None, description="Search in title/description"),
) -> list[Recipe]:
    """List recipes with pagination and optional keyword search.

    Args:
        session: Database session from dependency injection.
        offset: Number of items to skip for pagination.
        limit: Maximum number of items to return (1-1000).
        q: Optional search query to filter by title or description.

    Returns:
        List of recipes matching the criteria, ordered by created_at desc.

    """
    query = select(Recipe).order_by(col(Recipe.created_at).desc())

    if q:
        query = query.where(
            col(Recipe.title).contains(q) | col(Recipe.description).contains(q),
        )

    query = query.offset(offset).limit(limit)
    return list(session.exec(query).all())


@router.get(
    "/{recipe_id}",
    response_model=RecipePublic,
    summary="Get a single recipe",
)
def get_recipe(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
) -> Recipe:
    """Get a single recipe by ID.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to retrieve.

    Returns:
        The requested recipe.

    Raises:
        HTTPException: 404 if recipe not found.

    """
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe


@router.patch(
    "/{recipe_id}",
    response_model=RecipePublic,
    summary="Update a recipe (partial)",
)
def update_recipe(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    recipe: RecipeUpdate,
) -> Recipe:
    """Update a recipe with partial data.

    Only provided fields will be updated. Rating and notes should be
    updated via their dedicated endpoints.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to update.
        recipe: Partial recipe data for update.

    Returns:
        The updated recipe.

    Raises:
        HTTPException: 404 if recipe not found.

    """
    db_recipe = session.get(Recipe, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    update_data = recipe.model_dump(exclude_unset=True)
    db_recipe.sqlmodel_update(update_data)
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recipe",
)
def delete_recipe(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
) -> None:
    """Delete a recipe by ID.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to delete.

    Raises:
        HTTPException: 404 if recipe not found.

    """
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    session.delete(recipe)
    session.commit()
