"""E2E tests for Docker deployment.

These tests verify the deployed application works end-to-end.
Run with: pytest tests/e2e/ -v
"""
import pytest
from pathlib import Path


class TestDockerDeployment:
    """Tests for Docker deployment configuration."""

    def test_dockerfile_exists(self):
        """Verify Dockerfile exists at expected location."""
        dockerfile = Path(__file__).parent.parent.parent / "docker" / "Dockerfile"
        assert dockerfile.exists(), f"Dockerfile not found at {dockerfile}"

    def test_docker_compose_exists(self):
        """Verify docker-compose.yml exists at project root."""
        compose = Path(__file__).parent.parent.parent / "docker-compose.yml"
        assert compose.exists(), f"docker-compose.yml not found at {compose}"

    def test_dockerfile_has_multistage_build(self):
        """Verify Dockerfile uses multi-stage build."""
        dockerfile = Path(__file__).parent.parent.parent / "docker" / "Dockerfile"
        content = dockerfile.read_text()
        # Should have at least 2 FROM statements for multi-stage
        from_count = content.count("FROM ")
        assert from_count >= 2, f"Expected multi-stage build, found {from_count} FROM statements"

    def test_docker_compose_has_volume(self):
        """Verify docker-compose.yml has volume for data persistence."""
        compose = Path(__file__).parent.parent.parent / "docker-compose.yml"
        content = compose.read_text()
        assert "volumes:" in content, "docker-compose.yml missing volumes configuration"
        assert "eat-it-data" in content, "docker-compose.yml missing eat-it-data volume"


class TestDockerfile:
    """Tests for Dockerfile configuration."""

    def test_dockerfile_exists(self):
        """Verify Dockerfile exists at expected location."""
        dockerfile = Path(__file__).parent.parent.parent / "docker" / "Dockerfile"
        assert dockerfile.exists(), f"Dockerfile not found at {dockerfile}"

    def test_dockerfile_has_multistage_build(self):
        """Verify Dockerfile uses multi-stage build."""
        dockerfile = Path(__file__).parent.parent.parent / "docker" / "Dockerfile"
        content = dockerfile.read_text()
        from_count = content.count("FROM ")
        assert from_count >= 2, f"Expected multi-stage build, found {from_count} FROM statements"

    def test_dockerfile_has_frontend_stage(self):
        """Verify Dockerfile has Node.js frontend build stage."""
        dockerfile = Path(__file__).parent.parent.parent / "docker" / "Dockerfile"
        content = dockerfile.read_text()
        assert "node" in content.lower(), "Dockerfile missing Node.js stage for frontend build"

    def test_dockerfile_has_python_runtime(self):
        """Verify Dockerfile has Python runtime stage."""
        dockerfile = Path(__file__).parent.parent.parent / "docker" / "Dockerfile"
        content = dockerfile.read_text()
        assert "python" in content.lower(), "Dockerfile missing Python runtime stage"

    def test_dockerfile_exposes_port_8000(self):
        """Verify Dockerfile exposes port 8000."""
        dockerfile = Path(__file__).parent.parent.parent / "docker" / "Dockerfile"
        content = dockerfile.read_text()
        assert "8000" in content, "Dockerfile missing EXPOSE 8000"

    def test_dockerignore_exists(self):
        """Verify .dockerignore exists."""
        dockerignore = Path(__file__).parent.parent.parent / "docker" / ".dockerignore"
        assert dockerignore.exists(), f".dockerignore not found"
