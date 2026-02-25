"""Pydantic schemas for Recipe API request/response validation.

Follows CONTEXT.md constraints:
- Only title is required for creation
- Strict validation (no lenient coercion)
- Rating must be 1-5
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    """Base fields shared across recipe schemas."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    instructions: str = Field(..., min_length=1)
    prep_time: Optional[int] = Field(None, ge=0, description="Preparation time in minutes")
    cook_time: Optional[int] = Field(None, ge=0, description="Cooking time in minutes")
    servings: Optional[int] = Field(None, ge=1, description="Number of servings")
    source_url: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = Field(None, max_length=2000)
    tags: list[str] = Field(default_factory=list)


class RecipeCreate(RecipeBase):
    """Schema for creating a new recipe via POST.

    Per CONTEXT.md: Only title and instructions are required.
    All other fields are optional for maximum flexibility.
    """

    pass


class RecipeUpdate(BaseModel):
    """Schema for partial recipe update via PATCH.

    All fields are optional for partial updates.
    Only provided fields will be updated.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    instructions: Optional[str] = Field(None, min_length=1)
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    source_url: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = Field(None, max_length=2000)
    tags: Optional[list[str]] = None


class RecipeRatingUpdate(BaseModel):
    """Schema for updating recipe rating via dedicated endpoint.

    Per CONTEXT.md: Rating has a dedicated PATCH endpoint.
    """

    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5 stars, null to clear")


class RecipeNotesUpdate(BaseModel):
    """Schema for updating recipe notes via dedicated endpoint.

    Per CONTEXT.md: Notes has a dedicated PATCH endpoint.
    """

    notes: Optional[str] = Field(None, max_length=10000, description="Private notes, null to clear")


class RecipePublic(RecipeBase):
    """Schema for recipe response data.

    Includes all fields from RecipeBase plus id, user annotations,
    and timestamps.
    """

    id: int
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
