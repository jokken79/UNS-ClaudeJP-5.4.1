"""add performance indexes

Revision ID: 2025_11_06_perf_idx
Revises: e8f3b9c41a2e
Create Date: 2025-11-06 12:00:00.000000

Add performance indexes for frequently searched columns to improve query performance.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_06_perf_idx'
down_revision: str | None = 'e8f3b9c41a2e'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    """Create performance indexes for frequently queried columns"""

    # 1. Candidates - búsqueda frecuente por nombre
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_candidates_name
        ON candidates (full_name_kanji)
    """)

    # 2. Candidates - filtrado por status y fecha (composite index)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_candidates_status_date
        ON candidates (status, reception_date)
    """)

    # 3. Employees - join frecuente con factories
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_employees_factory
        ON employees (factory_id)
    """)

    # 4. Timer Cards - búsqueda por empleado y fecha (composite index)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_timer_cards_employee_date
        ON timer_cards (employee_id, work_date)
    """)

    # 5. Audit Log - búsqueda por tabla y timestamp (composite index)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_audit_log_table_timestamp
        ON audit_log (table_name, timestamp)
    """)

    print("✅ Performance indexes created successfully:")
    print("  - ix_candidates_name: candidates(full_name_kanji)")
    print("  - ix_candidates_status_date: candidates(status, reception_date)")
    print("  - ix_employees_factory: employees(factory_id)")
    print("  - ix_timer_cards_employee_date: timer_cards(employee_id, work_date)")
    print("  - ix_audit_log_table_timestamp: audit_log(table_name, timestamp)")


def downgrade():
    """Remove performance indexes"""

    op.execute("DROP INDEX IF EXISTS ix_audit_log_table_timestamp")
    op.execute("DROP INDEX IF EXISTS ix_timer_cards_employee_date")
    op.execute("DROP INDEX IF EXISTS ix_employees_factory")
    op.execute("DROP INDEX IF EXISTS ix_candidates_status_date")
    op.execute("DROP INDEX IF EXISTS ix_candidates_name")

    print("✅ Performance indexes removed successfully")
