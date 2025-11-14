"""add soft delete columns

Revision ID: 2025_11_06_soft_delete
Revises: 2025_11_06_perf_idx
Create Date: 2025-11-06 14:00:00.000000

Add deleted_at columns for soft delete functionality to candidates, employees, and factories tables.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_06_soft_delete'
down_revision: str | None = '2025_11_06_perf_idx'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    """Add deleted_at columns for soft delete"""

    # Add deleted_at to candidates table
    op.execute("""
        ALTER TABLE candidates
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE NULL
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_candidates_deleted_at
        ON candidates (deleted_at)
    """)

    # Add deleted_at to employees table
    op.execute("""
        ALTER TABLE employees
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE NULL
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_employees_deleted_at
        ON employees (deleted_at)
    """)

    # Add deleted_at to factories table
    op.execute("""
        ALTER TABLE factories
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE NULL
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_factories_deleted_at
        ON factories (deleted_at)
    """)

    print("✅ Soft delete columns and indexes created successfully:")
    print("  - candidates.deleted_at (indexed)")
    print("  - employees.deleted_at (indexed)")
    print("  - factories.deleted_at (indexed)")


def downgrade():
    """Remove soft delete columns"""

    # Drop indexes
    op.execute("DROP INDEX IF EXISTS ix_factories_deleted_at")
    op.execute("DROP INDEX IF EXISTS ix_employees_deleted_at")
    op.execute("DROP INDEX IF EXISTS ix_candidates_deleted_at")

    # Drop columns
    op.execute("ALTER TABLE factories DROP COLUMN IF EXISTS deleted_at")
    op.execute("ALTER TABLE employees DROP COLUMN IF EXISTS deleted_at")
    op.execute("ALTER TABLE candidates DROP COLUMN IF EXISTS deleted_at")

    print("✅ Soft delete columns and indexes removed successfully")
