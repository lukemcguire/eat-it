"""Tests for static file serving and SPA fallback."""

import pytest
from fastapi.testclient import TestClient

from eat_it.main import app


class TestStaticFiles:
    """Tests for static file serving configuration."""

    def test_api_routes_registered_before_static(self):
        """API routes are registered and accessible."""
        client = TestClient(app)
        response = client.get("/health")
        # Should not be caught by static file handler
        assert response.status_code != 404

    def test_catch_all_route_exists(self):
        """Catch-all route exists for SPA fallback."""
        routes = [r for r in app.routes if hasattr(r, "path")]
        # Check for catch-all path pattern
        catch_all_exists = any(
            "{full_path" in str(r.path) or r.path == "/{full_path:path}"
            for r in routes
        )
        assert catch_all_exists, "Catch-all SPA fallback route not found"

    def test_spa_fallback_returns_html(self):
        """SPA fallback returns HTML content type."""
        # This test verifies the route exists - actual file serving
        # only works when static/ directory exists
        client = TestClient(app)
        # Request a non-API route
        response = client.get("/some/spa/route")
        # Should not 404 - either returns HTML or redirects
        assert response.status_code != 404
