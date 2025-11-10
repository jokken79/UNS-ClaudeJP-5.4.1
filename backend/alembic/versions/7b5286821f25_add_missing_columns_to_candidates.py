"""add_missing_columns_to_candidates

Revision ID: 7b5286821f25
Revises: d49ae3cbfac6
Create Date: 2025-10-19 02:29:58.117908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


def _column_exists(table_name: str, column_name: str) -> bool:
    """Return True if the given column exists in the provided table."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [column["name"] for column in inspector.get_columns(table_name)]
    return column_name in columns


# revision identifiers, used by Alembic.
revision: str = '7b5286821f25'
down_revision: Union[str, None] = 'd49ae3cbfac6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the missing arrival_date column to candidates table if it doesn't exist
    if not _column_exists("candidates", "arrival_date"):
        op.add_column('candidates', sa.Column('arrival_date', sa.Date(), nullable=True))


def downgrade() -> None:
    # Remove the arrival_date column only if it exists
    if _column_exists("candidates", "arrival_date"):
        op.drop_column('candidates', 'arrival_date')
