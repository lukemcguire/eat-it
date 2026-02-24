"""Settings model for application configuration storage."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON, Index
from sqlmodel import Field, SQLModel


class Settings(SQLModel, table=True):
    """Key-value store for application settings.

    This is a flexible configuration store for app settings like
    embedding model info, user preferences, etc.

    Example:
        key="embedding_model", value={"name": "all-MiniLM-L6-v2", "version": "..."}

    Attributes:
        id: Primary key.
        key: Unique setting key (indexed).
        value: JSON value for the setting.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    __tablename__ = "settings"
    __table_args__ = (Index("ix_settings_key", "key", unique=True),)

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str  # Unique, indexed
    value: dict = Field(sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
