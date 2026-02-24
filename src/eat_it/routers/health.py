"""Health check router for application status."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check(request: Request) -> dict[str, str]:
    """Health check endpoint.

    Returns status information about the application including
    database connectivity and embedding model availability.

    Returns:
        Dict with status, database, and embedding_model fields.
    """
    # Check database connectivity by accessing app state
    database_status = "connected"
    if not hasattr(request.app.state, "db_initialized"):
        database_status = "not_initialized"

    # Check embedding model is loaded
    model_status = "loaded"
    if not hasattr(request.app.state, "embedding_model"):
        model_status = "not_loaded"

    return {
        "status": "healthy",
        "database": database_status,
        "embedding_model": model_status,
    }
