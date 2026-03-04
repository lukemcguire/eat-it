"""Store section model for organizing shopping list items."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class StoreSection(SQLModel, table=True):
    """Store section for organizing shopping list items.

    Predefined defaults provide common grocery store sections.
    Users can add custom sections as needed.

    Attributes:
        id: Primary key.
        name: Section name (e.g., "Produce", "Dairy").
        sort_order: Order for display sorting.
        is_default: Whether this is a predefined default section.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    __tablename__ = "store_sections"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    sort_order: int = 99
    is_default: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
