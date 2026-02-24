"""Initial migration with all core tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-02-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables with proper indexes."""
    # Create recipes table
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("instructions", sa.String(), nullable=False),
        sa.Column("prep_time", sa.Integer(), nullable=True),
        sa.Column("cook_time", sa.Integer(), nullable=True),
        sa.Column("servings", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_recipes_source_url", "recipes", ["source_url"])
    op.create_index("ix_recipes_created_at", "recipes", ["created_at"])

    # Create ingredient_groups table
    op.create_table(
        "ingredient_groups",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Create ingredients table
    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("ingredient_groups.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("preparation", sa.String(), nullable=True),
        sa.Column("raw", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Create shopping_lists table
    op.create_table(
        "shopping_lists",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("share_token", sa.String(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Create shopping_list_items table
    op.create_table(
        "shopping_list_items",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column(
            "shopping_list_id",
            sa.Integer(),
            sa.ForeignKey("shopping_lists.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Create settings table
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_settings_key", "settings", ["key"], unique=True)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index("ix_settings_key", table_name="settings")
    op.drop_table("settings")

    op.drop_table("shopping_list_items")
    op.drop_table("shopping_lists")

    op.drop_table("ingredients")
    op.drop_table("ingredient_groups")

    op.drop_index("ix_recipes_created_at", table_name="recipes")
    op.drop_index("ix_recipes_source_url", table_name="recipes")
    op.drop_table("recipes")
