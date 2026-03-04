"""add_recipe_embeddings

Revision ID: 0d96f8345dfd
Revises: 41be2253683d
Create Date: 2026-03-03 16:14:27.175035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d96f8345dfd'
down_revision: Union[str, None] = '41be2253683d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create vec0 virtual table for recipe embeddings
    # 384 dimensions for all-MiniLM-L6-v2 model
    op.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS recipe_embeddings "
        "USING vec0(embedding FLOAT[384])"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS recipe_embeddings")
