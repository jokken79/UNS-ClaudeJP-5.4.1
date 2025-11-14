"""remove duplicate building_name column

Revision ID: 3c7e9f2b8a4d
Revises: ab12cd34ef56
Create Date: 2025-10-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


# revision identifiers, used by Alembic.
revision: str = '3c7e9f2b8a4d'
down_revision: str | None = 'ab12cd34ef56'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    """Remove duplicate building_name column from candidates table.

    This column was redundant with address_building which contains the same data.
    All references have been updated to use address_building instead.
    """
    # Drop the duplicate column
    if _column_exists('candidates', 'building_name'):
        op.drop_column('candidates', 'building_name')


def downgrade():
    """Restore building_name column if needed for rollback."""
    # Add the column back as nullable
    if not _column_exists('candidates', 'building_name'):
        op.add_column('candidates', sa.Column('building_name', sa.String(length=100), nullable=True))
