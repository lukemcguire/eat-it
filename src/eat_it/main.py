"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from eat_it.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown."""
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Cleanup (SQLite handles connection cleanup automatically)


app = FastAPI(
    title="Eat It",
    description="Recipe Storage and Smart Shopping List",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
