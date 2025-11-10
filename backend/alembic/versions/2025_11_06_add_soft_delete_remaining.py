"""add soft delete to remaining entities

Revision ID: 2025_11_06_soft_del_rem
Revises: 2025_11_06_soft_delete
Create Date: 2025-11-06 16:00:00.000000

Add deleted_at columns for soft delete functionality to apartments, contract_workers, staff, and contracts tables.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_06_soft_del_rem'
down_revision: str | None = '2025_11_06_soft_delete'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    """Add deleted_at columns for soft delete to remaining entities"""

    # 1. Apartments
    op.execute("""
        ALTER TABLE apartments
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE NULL
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_apartments_deleted_at
        ON apartments (deleted_at)
    """)

    # 2. Contract Workers
    op.execute("""
        ALTER TABLE contract_workers
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE NULL
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_contract_workers_deleted_at
        ON contract_workers (deleted_at)
    """)

    # 3. Staff
    op.execute("""
        ALTER TABLE staff
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE NULL
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_staff_deleted_at
        ON staff (deleted_at)
    """)

    # 4. Contracts
    op.execute("""
        ALTER TABLE contracts
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE NULL
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_contracts_deleted_at
        ON contracts (deleted_at)
    """)


def downgrade():
    """Remove soft delete columns"""
    op.execute("DROP INDEX IF EXISTS ix_contracts_deleted_at")
    op.execute("DROP INDEX IF EXISTS ix_staff_deleted_at")
    op.execute("DROP INDEX IF EXISTS ix_contract_workers_deleted_at")
    op.execute("DROP INDEX IF EXISTS ix_apartments_deleted_at")

    op.execute("ALTER TABLE contracts DROP COLUMN IF EXISTS deleted_at")
    op.execute("ALTER TABLE staff DROP COLUMN IF EXISTS deleted_at")
    op.execute("ALTER TABLE contract_workers DROP COLUMN IF EXISTS deleted_at")
    op.execute("ALTER TABLE apartments DROP COLUMN IF EXISTS deleted_at")
