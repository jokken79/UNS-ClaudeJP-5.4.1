"""add_photo_data_url_to_contract_workers_and_staff

Revision ID: a7b3c4d5e6f7
Revises: fe6aac62e522
Create Date: 2025-10-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


# revision identifiers, used by Alembic.
revision: str = 'a7b3c4d5e6f7'
down_revision: Union[str, None] = '3c7e9f2b8a4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add photo_data_url column to contract_workers table
    if not _column_exists('contract_workers', 'photo_data_url'):
        op.add_column('contract_workers', sa.Column('photo_data_url', sa.Text(), nullable=True))

    # Add photo_data_url column to staff table
    if not _column_exists('staff', 'photo_data_url'):
        op.add_column('staff', sa.Column('photo_data_url', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove the columns if rolling back
    if _column_exists('staff', 'photo_data_url'):
        op.drop_column('staff', 'photo_data_url')
    if _column_exists('contract_workers', 'photo_data_url'):
        op.drop_column('contract_workers', 'photo_data_url')
