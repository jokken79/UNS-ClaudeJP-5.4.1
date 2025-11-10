"""add_missing_candidate_columns_simple

Revision ID: fe6aac62e522
Revises: ef4a15953791
Create Date: 2025-10-24 00:26:15.994355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


# revision identifiers, used by Alembic.
revision: str = 'fe6aac62e522'
down_revision: Union[str, None] = 'ef4a15953791'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to candidates table
    if not _column_exists('candidates', 'photo_data_url'):
        op.add_column('candidates', sa.Column('photo_data_url', sa.Text(), nullable=True))
    if not _column_exists('candidates', 'lunch_preference'):
        op.add_column('candidates', sa.Column('lunch_preference', sa.String(length=50), nullable=True))
    if not _column_exists('candidates', 'glasses'):
        op.add_column('candidates', sa.Column('glasses', sa.String(length=100), nullable=True))
    if not _column_exists('candidates', 'ocr_notes'):
        op.add_column('candidates', sa.Column('ocr_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove the columns if rolling back
    if _column_exists('candidates', 'ocr_notes'):
        op.drop_column('candidates', 'ocr_notes')
    if _column_exists('candidates', 'glasses'):
        op.drop_column('candidates', 'glasses')
    if _column_exists('candidates', 'lunch_preference'):
        op.drop_column('candidates', 'lunch_preference')
    if _column_exists('candidates', 'photo_data_url'):
        op.drop_column('candidates', 'photo_data_url')
