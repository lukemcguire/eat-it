"""add ingredient display_order

Revision ID: 1e4d96d3d1a3
Revises: 997bbdccf6f4
Create Date: 2026-03-04 12:06:01.977456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '1e4d96d3d1a3'
down_revision: Union[str, None] = '997bbdccf6f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add display_order column with default value 0
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'display_order',
                sa.Integer(),
                nullable=False,
                server_default=text('0')
            )
        )


def downgrade() -> None:
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.drop_column('display_order')
