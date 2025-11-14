"""Add photo_data_url column to employees table

Revision ID: 2025_10_26_001
Revises:
Create Date: 2025-10-26 13:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '2025_10_26_add_employee_photo_data_url'
down_revision: str | None = 'a7b3c4d5e6f7'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check if employees table exists
    tables = inspector.get_table_names()
    if 'employees' not in tables:
        print("⚠️  employees table does not exist, skipping photo_data_url column creation")
        return

    # Check if photo_data_url column already exists
    columns = [col['name'] for col in inspector.get_columns('employees')]

    if 'photo_data_url' not in columns:
        print("✅ Adding photo_data_url column to employees table")
        op.add_column('employees', sa.Column('photo_data_url', sa.Text(), nullable=True))
    else:
        print("✅ photo_data_url column already exists in employees table")


def downgrade() -> None:
    # Get database connection and inspector
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check if employees table exists
    tables = inspector.get_table_names()
    if 'employees' not in tables:
        print("⚠️  employees table does not exist, skipping photo_data_url column removal")
        return

    # Check if photo_data_url column exists before dropping
    columns = [col['name'] for col in inspector.get_columns('employees')]

    if 'photo_data_url' in columns:
        print("✅ Dropping photo_data_url column from employees table")
        op.drop_column('employees', 'photo_data_url')
    else:
        print("✅ photo_data_url column does not exist in employees table")
