"""add_store_sections

Revision ID: 997bbdccf6f4
Revises: 0d96f8345dfd
Create Date: 2026-03-04 01:15:30.777053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '997bbdccf6f4'
down_revision: Union[str, None] = '0d96f8345dfd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create store_sections table
    op.create_table(
        'store_sections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='99'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default sections with proper sort_order
    op.execute("""
        INSERT INTO store_sections (name, sort_order, is_default, created_at, updated_at)
        VALUES
            ('Produce', 1, 1, datetime('now'), datetime('now')),
            ('Dairy', 2, 1, datetime('now'), datetime('now')),
            ('Meat', 3, 1, datetime('now'), datetime('now')),
            ('Bakery', 4, 1, datetime('now'), datetime('now')),
            ('Pantry', 5, 1, datetime('now'), datetime('now')),
            ('Frozen', 6, 1, datetime('now'), datetime('now')),
            ('Other', 99, 1, datetime('now'), datetime('now'))
    """)

    # Add section_id and display_order columns to shopping_list_items
    op.add_column(
        'shopping_list_items',
        sa.Column('section_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_shopping_list_items_section_id',
        'shopping_list_items',
        'store_sections',
        ['section_id'],
        ['id']
    )
    op.add_column(
        'shopping_list_items',
        sa.Column('display_order', sa.Integer(), nullable=True)
    )

    # Add expires_at column to shopping_lists
    op.add_column(
        'shopping_lists',
        sa.Column('expires_at', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    # Drop expires_at from shopping_lists
    op.drop_column('shopping_lists', 'expires_at')

    # Drop display_order and section_id from shopping_list_items
    op.drop_column('shopping_list_items', 'display_order')
    op.drop_constraint('fk_shopping_list_items_section_id', 'shopping_list_items', type_='foreignkey')
    op.drop_column('shopping_list_items', 'section_id')

    # Drop store_sections table
    op.drop_table('store_sections')
