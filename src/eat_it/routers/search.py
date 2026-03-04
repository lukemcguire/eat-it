"""Search endpoint with semantic and keyword fallback.

Provides the /search endpoint that:
1. Tries semantic search first if embedding model is available
2. Falls back to keyword LIKE search if no semantic results
3. Returns list[RecipePublic]

Semantic search uses sqlite-vec KNN (k-nearest neighbors) via
the recipe_embeddings virtual table.
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session, col, select

from eat_it.database import get_session
from eat_it.models.recipe import Recipe
from eat_it.schemas.recipe import RecipePublic
from eat_it.services.embedding import generate_embedding, serialize_f32

router = APIRouter(tags=["search"])

# Distance threshold for semantic relevance (L2 distance)
# Lower = more similar. 1.5 is a reasonable cutoff for recipe matching.
SEMANTIC_DISTANCE_THRESHOLD = 1.5


@router.get("/search", response_model=list[RecipePublic])
def search_recipes(
    *,
    session: Session = Depends(get_session),
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
) -> list[Recipe]:
    """Search recipes using semantic or keyword search.

    Tries semantic search first if embedding model is available.
    Falls back to keyword search if no semantic results or on error.

    Args:
        session: Database session from dependency injection.
        request: FastAPI request for accessing app.state.embedding_model.
        q: Search query string (required, min 1 character).
        limit: Maximum results to return (default 20, max 100).

    Returns:
        List of recipes matching the search query, ordered by relevance.
        For semantic search, results are ordered by embedding distance.
        For keyword search, results are unordered.

    """
    results: list[Recipe] = []

    # 1. Try semantic search if model available
    if request.app.state.embedding_model:
        try:
            query_embedding = generate_embedding(
                q, request.app.state.embedding_model
            )
            query_binary = serialize_f32(query_embedding)

            conn = session.connection().connection.dbapi_connection
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT rowid as recipe_id, distance
                FROM recipe_embeddings
                WHERE embedding MATCH ?
                ORDER BY distance
                LIMIT ?
                """,
                [query_binary, limit],
            )
            rows = cursor.fetchall()
            cursor.close()

            if rows:
                # Filter by distance threshold (L2 distance)
                recipe_ids = [
                    r[0] for r in rows if r[1] < SEMANTIC_DISTANCE_THRESHOLD
                ]

                if recipe_ids:
                    # Fetch recipes preserving KNN order
                    id_to_distance = {
                        r[0]: r[1] for r in rows if r[1] < SEMANTIC_DISTANCE_THRESHOLD
                    }
                    recipes = session.exec(
                        select(Recipe).where(Recipe.id.in_(recipe_ids))
                    ).all()
                    results = sorted(
                        recipes,
                        key=lambda r: id_to_distance.get(r.id, float("inf")),
                    )
        except Exception:
            pass  # Fall through to keyword search

    # 2. Fallback to keyword search
    if not results:
        results = list(
            session.exec(
                select(Recipe)
                .where(
                    col(Recipe.title).contains(q)
                    | col(Recipe.description).contains(q)
                    | col(Recipe.instructions).contains(q)
                )
                .limit(limit)
            ).all()
        )

    return results
