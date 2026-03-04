"""Pydantic schemas for Shopping List API request/response validation.

Follows CONTEXT.md constraints:
- Shopping lists can be created empty or from recipes
- Items are auto-categorized to store sections
- Strict validation (no lenient coercion)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ShoppingListItemBase(BaseModel):
    """Base fields shared across shopping list item schemas."""

    name: str = Field(..., min_length=1, max_length=500)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=100)
    section_id: Optional[int] = None
    display_order: Optional[int] = Field(None, ge=0)
    checked: bool = False


class ShoppingListItemCreate(ShoppingListItemBase):
    """Schema for creating a new shopping list item via POST.

    Per plan: section_id is optional; auto-categorized if not provided.
    """

    pass


class ShoppingListItemUpdate(BaseModel):
    """Schema for partial shopping list item update via PATCH.

    All fields are optional for partial updates.
    Only provided fields will be updated.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=100)
    section_id: Optional[int] = None
    display_order: Optional[int] = Field(None, ge=0)
    checked: Optional[bool] = None


class ShoppingListItemPublic(ShoppingListItemBase):
    """Schema for shopping list item response data.

    Includes all fields from ShoppingListItemBase plus id and shopping_list_id.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    shopping_list_id: int


class ShoppingListBase(BaseModel):
    """Base fields shared across shopping list schemas."""

    name: str = Field(..., min_length=1, max_length=200)


class ShoppingListCreate(ShoppingListBase):
    """Schema for creating a new shopping list via POST.

    Per plan: Can optionally include recipe_ids for generation.
    """

    recipe_ids: Optional[list[int]] = None


class ShoppingListUpdate(BaseModel):
    """Schema for partial shopping list update via PATCH.

    All fields are optional for partial updates.
    Only provided fields will be updated.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=200)


class ShoppingListPublic(ShoppingListBase):
    """Schema for shopping list response data.

    Includes all fields from ShoppingListBase plus id, share_token,
    expiration, items, and timestamps.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    share_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    items: list[ShoppingListItemPublic] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ShoppingListGenerate(BaseModel):
    """Schema for generating a shopping list from recipes.

    Per CONTEXT.md: Select recipes, get a combined shopping list.
    """

    name: str = Field(..., min_length=1, max_length=200)
    recipe_ids: list[int] = Field(..., min_length=1)


class ShoppingListsPublic(BaseModel):
    """Schema for listing multiple shopping lists.

    Per plan: Returns all lists without nested items for performance.
    """

    data: list[ShoppingListPublic]
    count: int
