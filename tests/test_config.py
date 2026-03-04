"""Tests for config module."""

import pytest

from eat_it.config import Settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_port_defaults_to_8000(self):
        """Settings.port defaults to 8000."""
        settings = Settings()
        assert settings.port == 8000

    def test_environment_defaults_to_production(self):
        """Settings.environment defaults to production."""
        settings = Settings()
        assert settings.environment == "production"

    def test_port_can_be_overridden(self, monkeypatch):
        """Settings.port can be overridden via EAT_IT_PORT."""
        monkeypatch.setenv("EAT_IT_PORT", "3000")
        settings = Settings()
        assert settings.port == 3000

    def test_environment_can_be_overridden(self, monkeypatch):
        """Settings.environment can be overridden via EAT_IT_ENVIRONMENT."""
        monkeypatch.setenv("EAT_IT_ENVIRONMENT", "development")
        settings = Settings()
        assert settings.environment == "development"
