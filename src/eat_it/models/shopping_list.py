"""Shopping List models for collaborative list management."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class ShoppingListItem(SQLModel, table=True):
    """Individual item in a shopping list.

    Items are generated from recipes but become independent
    (no back-link to source recipe).

    Attributes:
        id: Primary key.
        shopping_list_id: Foreign key to shopping list.
        name: Item name.
        quantity: Optional quantity.
        unit: Optional unit of measurement.
        checked: Whether item has been checked off.
        section_id: Foreign key to store section for organization.
        display_order: Order for manual reordering within section.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    __tablename__ = "shopping_list_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    shopping_list_id: int = Field(foreign_key="shopping_lists.id")
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    checked: bool = False
    section_id: Optional[int] = Field(default=None, foreign_key="store_sections.id")
    display_order: Optional[int] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ShoppingList(SQLModel, table=True):
    """Shopping list with optional sharing capabilities.

    Attributes:
        id: Primary key.
        name: List name.
        share_token: Token for sharing via link/PIN.
        expires_at: Optional expiration time for share token.
        metadata_: Versioned metadata for plugin extensibility.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    __tablename__ = "shopping_lists"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    share_token: Optional[str] = None  # For sharing via link/PIN
    expires_at: Optional[datetime] = None  # Share token expiration

    # Versioned metadata for plugin extensibility (ARCH-03)
    # Structure: {"version": 1, "data": {...plugin-specific data...}}
    # Note: Using metadata_ as field name because SQLAlchemy reserves 'metadata'
    metadata_: dict = Field(
        default_factory=lambda: {"version": 1, "data": {}},
        sa_column=Column("metadata", JSON),
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
