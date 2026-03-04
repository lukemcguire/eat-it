"""Recipe CRUD endpoints with FastAPI and SQLModel.

Provides RESTful endpoints for recipe management:
- POST /recipes - Create a new recipe
- GET /recipes - List recipes with pagination and search
- GET /recipes/export - Export all recipes as JSON or CSV
- GET /recipes/parse - Parse a recipe URL
- GET /recipes/{recipe_id} - Get a single recipe
- PATCH /recipes/{recipe_id} - Update a recipe (partial)
- DELETE /recipes/{recipe_id} - Delete a recipe

Note: Rating and notes updates are handled by separate endpoints
(PATCH /recipes/{id}/rating, PATCH /recipes/{id}/notes) per CONTEXT.md
decision "Separate annotation endpoints".
"""

import csv
import io
import json
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, col, select

from eat_it.database import get_session
from eat_it.models.recipe import Recipe
from eat_it.schemas.recipe import (
    RecipeCreate,
    RecipeNotesUpdate,
    RecipePublic,
    RecipeRatingUpdate,
    RecipeUpdate,
)
from eat_it.services.recipe_parser import ParseErrorCode, ParseResult, RecipeParser

router = APIRouter(tags=["recipes"])


# ─── Parse Endpoint Response Models ─────────────────────────────────────


class ParseErrorData(BaseModel):
    """Error data returned when parsing fails."""

    code: str
    message: str
    suggested_action: str


class ParseDuplicateWarning(BaseModel):
    """Warning data when URL already exists in database."""

    existing_recipe: RecipePublic


class ParseResponse(BaseModel):
    """Response model for /parse endpoint."""

    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[ParseErrorData] = None
    duplicate_warning: Optional[ParseDuplicateWarning] = None


# ─── Parse Endpoint ─────────────────────────────────────────────────────


@router.get(
    "/parse",
    response_model=ParseResponse,
    summary="Parse a recipe URL",
)
async def parse_recipe_url(
    url: str = Query(..., description="Recipe URL to parse"),
    session: Session = Depends(get_session),
) -> ParseResponse:
    """Parse a recipe URL and return structured data.

    Fetches the URL, extracts recipe data using recipe-scrapers,
    and checks for duplicate URLs in the database.

    Args:
        url: The recipe URL to parse.
        session: Database session for duplicate detection.

    Returns:
        ParseResponse with:
        - On success: parsed recipe data in 'data' field
        - On duplicate: 'duplicate_warning' with existing recipe
        - On failure: 'error' with code, message, and suggested action

    """
    # Check for existing recipe with this source_url (duplicate detection)
    existing_recipe = session.exec(
        select(Recipe).where(Recipe.source_url == url)
    ).first()

    # Parse the URL
    parser = RecipeParser()
    result: ParseResult = await parser.parse_url(url)

    if not result.success:
        # Return error response
        return ParseResponse(
            success=False,
            error=ParseErrorData(
                code=result.error.code.value if result.error else ParseErrorCode.NO_RECIPE_FOUND.value,
                message=result.error.message if result.error else "Unknown error",
                suggested_action=result.error.suggested_action
                if result.error
                else "Try again or enter the recipe manually.",
            ),
        )

    # Success - build response
    response = ParseResponse(
        success=True,
        data=result.data,
    )

    # Add duplicate warning if URL already exists
    if existing_recipe:
        response.duplicate_warning = ParseDuplicateWarning(
            existing_recipe=RecipePublic.model_validate(existing_recipe)
        )

    return response


# ─── Export Endpoint ──────────────────────────────────────────────────────


@router.get(
    "/export",
    summary="Export all recipes",
)
def export_recipes(
    format: str = Query(..., pattern="^(json|csv)$", description="Export format"),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Export all recipes in JSON or CSV format.

    Downloads all recipes with all fields. Use for backup or migration.

    Args:
        format: Export format, either 'json' or 'csv'.
        session: Database session from dependency injection.

    Returns:
        StreamingResponse with file download:
        - JSON: Array of recipe objects
        - CSV: Header row + one row per recipe

    Note:
        - CSV escapes newlines in instructions as \\n
        - CSV joins tags with pipe character |
        - All recipe fields are included
    """
    recipes = session.exec(select(Recipe)).all()

    if format == "json":
        def generate_json():
            data = [recipe.model_dump() for recipe in recipes]
            yield json.dumps(data, indent=2, default=str)

        return StreamingResponse(
            generate_json(),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=recipes.json"},
        )

    else:  # format == "csv"
        def generate_csv():
            output = io.StringIO()
            writer = csv.writer(output)

            # Header row
            writer.writerow([
                "id", "title", "description", "instructions",
                "prep_time", "cook_time", "servings", "source_url",
                "image_url", "tags", "rating", "notes",
                "created_at", "updated_at",
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

            # Data rows
            for recipe in recipes:
                writer.writerow([
                    recipe.id,
                    recipe.title,
                    recipe.description or "",
                    recipe.instructions.replace("\n", "\\n"),
                    recipe.prep_time or "",
                    recipe.cook_time or "",
                    recipe.servings or "",
                    recipe.source_url or "",
                    recipe.image_url or "",
                    "|".join(recipe.tags or []),
                    recipe.rating or "",
                    recipe.notes or "",
                    recipe.created_at.isoformat() if recipe.created_at else "",
                    recipe.updated_at.isoformat() if recipe.updated_at else "",
                ])
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)

        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=recipes.csv"},
        )


# ─── CRUD Endpoints ──────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=RecipePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recipe",
)
def create_recipe(
    *,
    session: Session = Depends(get_session),
    request: Request,
    recipe: RecipeCreate,
) -> Recipe:
    """Create a new recipe manually or from parsed URL data.

    Args:
        session: Database session from dependency injection.
        request: FastAPI request object for accessing app state.
        recipe: Recipe data for creation.

    Returns:
        The created recipe with generated id and timestamps.

    """
    db_recipe = Recipe.model_validate(recipe)
    session.add(db_recipe)
    # Flush to get the recipe ID before commit
    session.flush()

    # Generate and store embedding (best effort, silent failure)
    # Do this BEFORE commit so it's part of the same transaction
    if request.app.state.embedding_model:
        try:
            from eat_it.services.embedding import (
                generate_embedding,
                recipe_to_text,
                serialize_f32,
            )

            text = recipe_to_text(db_recipe)
            embedding = generate_embedding(text, request.app.state.embedding_model)
            embedding_binary = serialize_f32(embedding)

            conn = session.connection().connection.dbapi_connection
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO recipe_embeddings(rowid, embedding) VALUES (?, ?)",
                [db_recipe.id, embedding_binary],
            )
            cursor.close()
        except Exception:
            pass  # Silent failure per CONTEXT.md

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


# ─── Annotation Endpoints ────────────────────────────────────────────────


@router.patch(
    "/{recipe_id}/rating",
    response_model=RecipePublic,
    summary="Update recipe rating",
)
def update_recipe_rating(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    rating_update: RecipeRatingUpdate,
) -> Recipe:
    """Update a recipe's rating.

    Per CONTEXT.md: Dedicated endpoint for rating updates only.
    Rating must be between 1 and 5, or null to clear.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to update.
        rating_update: Rating update payload.

    Returns:
        The updated recipe.

    Raises:
        HTTPException: 404 if recipe not found.

    """
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    recipe.rating = rating_update.rating
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@router.patch(
    "/{recipe_id}/notes",
    response_model=RecipePublic,
    summary="Update recipe notes",
)
def update_recipe_notes(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    notes_update: RecipeNotesUpdate,
) -> Recipe:
    """Update a recipe's notes.

    Per CONTEXT.md: Dedicated endpoint for notes updates only.
    Notes can be any text up to 10000 characters, or null to clear.

    Args:
        session: Database session from dependency injection.
        recipe_id: The ID of the recipe to update.
        notes_update: Notes update payload.

    Returns:
        The updated recipe.

    Raises:
        HTTPException: 404 if recipe not found.

    """
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    recipe.notes = notes_update.notes
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe
