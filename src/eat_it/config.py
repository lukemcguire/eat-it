"""Application configuration via Pydantic Settings.

Environment variables:
    EAT_IT_DATABASE_URL: SQLite database URL (default: sqlite:///./data/eat-it.db)
    EAT_IT_EMBEDDING_MODEL: Sentence transformer model name (default: all-MiniLM-L6-v2)
    EAT_IT_STATIC_DIR: Path to static files directory (default: /app/static for Docker)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EAT_IT_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./data/eat-it.db"
    embedding_model: str = "all-MiniLM-L6-v2"
    port: int = 8000
    environment: str = "production"
    static_dir: str = "/app/static"  # Docker default; override for local dev


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance for convenience
settings = Settings()

