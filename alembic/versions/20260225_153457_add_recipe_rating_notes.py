"""add_recipe_rating_notes

Revision ID: 41be2253683d
Revises: 001_initial
Create Date: 2026-02-25 15:34:57.644305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41be2253683d'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add rating and notes columns to recipes table
    # Using batch_alter_table for SQLite compatibility
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("rating", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove rating and notes columns from recipes table
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.drop_column("notes")
        batch_op.drop_column("rating")
