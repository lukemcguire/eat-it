"""Recipe and Ingredient models with structured ingredient parsing."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON, Index
from sqlmodel import Field, SQLModel


class Ingredient(SQLModel, table=True):
    """Single ingredient with structured parsing.

    Attributes:
        id: Primary key.
        group_id: Foreign key to ingredient group.
        quantity: Numeric amount (can be null for "salt to taste").
        unit: Unit of measurement (can be null for unit-less ingredients).
        name: Ingredient name.
        preparation: Preparation method (e.g., "diced", "minced").
        raw: Original unparsed ingredient string.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    __tablename__ = "ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="ingredient_groups.id")

    quantity: Optional[float] = None
    unit: Optional[str] = None  # Can be null ("salt to taste")
    name: str
    preparation: Optional[str] = None  # "diced", "minced", etc.
    raw: str  # Original unparsed string
    # Order within group (gaps allowed, no renumbering on delete)
    display_order: int = Field(default=0, ge=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IngredientGroup(SQLModel, table=True):
    """Group of ingredients (e.g., "For the sauce:").

    Attributes:
        id: Primary key.
        recipe_id: Foreign key to recipe.
        name: Group name (e.g., "For the sauce:").
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    __tablename__ = "ingredient_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipes.id")
    name: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Recipe(SQLModel, table=True):
    """Complete recipe with nested ingredient groups.

    Attributes:
        id: Primary key.
        title: Recipe title.
        description: Optional description.
        instructions: Cooking instructions.
        prep_time: Preparation time in minutes.
        cook_time: Cooking time in minutes.
        servings: Number of servings.
        source_url: Original recipe URL.
        image_url: Recipe image URL.
        tags: List of tags for categorization.
        rating: User rating (1-5 stars, nullable).
        notes: Private freeform notes (nullable).
        metadata_: Versioned metadata for plugin extensibility.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    __tablename__ = "recipes"
    __table_args__ = (
        Index("ix_recipes_source_url", "source_url"),
        Index("ix_recipes_created_at", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    instructions: str
    prep_time: Optional[int] = None  # Minutes
    cook_time: Optional[int] = None  # Minutes
    servings: Optional[int] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # User annotations
    rating: Optional[int] = Field(default=None, ge=1, le=5)  # 1-5 stars
    notes: Optional[str] = None  # Private freeform notes

    # Versioned metadata for plugin extensibility (ARCH-03)
    # Structure: {"version": 1, "data": {...plugin-specific data...}}
    # Note: Using metadata_ as field name because SQLAlchemy reserves 'metadata'
    metadata_: dict = Field(
        default_factory=lambda: {"version": 1, "data": {}},
        sa_column=Column("metadata", JSON),
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
