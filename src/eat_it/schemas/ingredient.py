"""Pydantic schemas for Ingredient API request/response validation.

Follows CONTEXT.md constraints:
- display_order for ordering within groups (gaps allowed)
- group_id required for ingredients (every ingredient belongs to a group)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IngredientGroupBase(BaseModel):
    """Base fields shared across ingredient group schemas."""

    name: Optional[str] = None


class IngredientGroupCreate(IngredientGroupBase):
    """Schema for creating a new ingredient group via POST."""

    pass


class IngredientGroupUpdate(BaseModel):
    """Schema for partial ingredient group update via PATCH.

    All fields are optional for partial updates.
    """

    name: Optional[str] = None


class IngredientGroupPublic(IngredientGroupBase):
    """Schema for ingredient group response data.

    Includes all fields from IngredientGroupBase plus id, recipe_id,
    and timestamps.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    recipe_id: int
    created_at: datetime
    updated_at: datetime


class IngredientBase(BaseModel):
    """Base fields shared across ingredient schemas."""

    quantity: Optional[float] = None
    unit: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=500)
    preparation: Optional[str] = None
    raw: str = Field(..., min_length=1)
    display_order: int = Field(0, ge=0)


class IngredientCreate(IngredientBase):
    """Schema for creating a new ingredient via POST.

    group_id is optional - if missing or invalid, a default "Ingredients"
    group is auto-created.
    """

    group_id: Optional[int] = None


class IngredientUpdate(BaseModel):
    """Schema for partial ingredient update via PATCH.

    All fields are optional for partial updates.
    group_id allows moving ingredient to a different group.
    """

    quantity: Optional[float] = None
    unit: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    preparation: Optional[str] = None
    raw: Optional[str] = Field(None, min_length=1)
    display_order: Optional[int] = Field(None, ge=0)
    group_id: Optional[int] = None


class IngredientPublic(IngredientBase):
    """Schema for ingredient response data.

    Includes all fields from IngredientBase plus id, group_id,
    and timestamps.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_at: datetime
    updated_at: datetime


class IngredientGroupWithIngredients(IngredientGroupPublic):
    """Schema for ingredient group with nested ingredients.

    Used for bulk operation responses.
    """

    ingredients: list[IngredientPublic] = Field(default_factory=list)


class IngredientBulkItem(BaseModel):
    """Schema for ingredient in bulk request payload.

    id is optional - null for new ingredients, existing id for updates.
    group_id not needed (derived from parent group).
    """

    id: Optional[int] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=500)
    preparation: Optional[str] = None
    raw: str = Field(..., min_length=1)
    display_order: int = Field(0, ge=0)


class IngredientGroupBulkItem(BaseModel):
    """Schema for ingredient group in bulk request payload.

    id is optional - null for new groups, existing id for updates.
    recipe_id not needed (derived from URL path).
    """

    id: Optional[int] = None
    name: Optional[str] = None
    ingredients: list[IngredientBulkItem] = Field(default_factory=list)


class IngredientsBulkRequest(BaseModel):
    """Schema for bulk replacement of all ingredients.

    Payload contains complete state of all groups with nested ingredients.
    Existing items include their id, new items have id: null.
    Groups/ingredients not in payload are deleted.
    """

    groups: list[IngredientGroupBulkItem]


class IngredientsBulkResponse(BaseModel):
    """Schema for bulk operation response.

    Returns the complete groups+ingredients structure after the operation.
    """

    groups: list[IngredientGroupWithIngredients]
