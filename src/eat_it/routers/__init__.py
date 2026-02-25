"""Routers for Eat It application."""

from eat_it.routers.health import router as health_router
from eat_it.routers.recipes import router as recipes_router

__all__ = ["health_router", "recipes_router"]
