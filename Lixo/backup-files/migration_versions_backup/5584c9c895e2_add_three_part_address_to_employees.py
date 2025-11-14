"""add_three_part_address_to_employees

Revision ID: 5584c9c895e2
Revises: a579f9a2a523
Create Date: 2025-10-24 09:19:00.241642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


# revision identifiers, used by Alembic.
revision: str = '5584c9c895e2'
down_revision: Union[str, None] = 'a579f9a2a523'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the 3 Japanese address columns to employees table
    if not _column_exists('employees', 'current_address'):
        op.add_column('employees', sa.Column('current_address', sa.String(), nullable=True))
    if not _column_exists('employees', 'address_banchi'):
        op.add_column('employees', sa.Column('address_banchi', sa.String(), nullable=True))
    if not _column_exists('employees', 'address_building'):
        op.add_column('employees', sa.Column('address_building', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove the 3 Japanese address columns from employees table
    if _column_exists('employees', 'address_building'):
        op.drop_column('employees', 'address_building')
    if _column_exists('employees', 'address_banchi'):
        op.drop_column('employees', 'address_banchi')
    if _column_exists('employees', 'current_address'):
        op.drop_column('employees', 'current_address')
