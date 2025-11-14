"""fix cascade rules for referential integrity

Revision ID: 2025_10_27_005
Revises: 2025_10_27_004
Create Date: 2025-10-27

This migration fixes foreign key CASCADE rules to ensure proper data cleanup
when parent records are deleted. It also adds missing foreign key constraints.

Estimated execution time: 2-3 minutes
Impact: Proper cleanup of related data, improved referential integrity
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_10_27_005'
down_revision: str | None = '2025_10_27_004'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    """Fix CASCADE rules and add missing foreign key constraints"""

    # Fix candidate_forms cascade - should delete forms when candidate is deleted
    op.execute("""
        ALTER TABLE candidate_forms DROP CONSTRAINT IF EXISTS candidate_forms_candidate_id_fkey
    """)
    op.execute("""
        ALTER TABLE candidate_forms ADD CONSTRAINT candidate_forms_candidate_id_fkey
        FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
    """)

    # Clean up orphaned timer_cards data before adding constraints
    op.execute("""
        UPDATE timer_cards SET employee_id = NULL
        WHERE employee_id NOT IN (SELECT id FROM employees)
    """)
    op.execute("""
        UPDATE timer_cards SET factory_id = NULL
        WHERE factory_id NOT IN (SELECT factory_id FROM factories)
    """)

    # Add foreign key constraints to timer_cards if they don't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_timer_cards_employee'
            ) THEN
                ALTER TABLE timer_cards ADD CONSTRAINT fk_timer_cards_employee
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_timer_cards_factory'
            ) THEN
                ALTER TABLE timer_cards ADD CONSTRAINT fk_timer_cards_factory
                FOREIGN KEY (factory_id) REFERENCES factories(factory_id);
            END IF;
        END $$;
    """)


def downgrade():
    """Revert CASCADE rules to original state"""

    # Revert candidate_forms cascade
    op.execute("""
        ALTER TABLE candidate_forms DROP CONSTRAINT IF EXISTS candidate_forms_candidate_id_fkey
    """)
    op.execute("""
        ALTER TABLE candidate_forms ADD CONSTRAINT candidate_forms_candidate_id_fkey
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    """)

    # Remove foreign key constraints from timer_cards
    op.execute("""
        ALTER TABLE timer_cards DROP CONSTRAINT IF EXISTS fk_timer_cards_employee
    """)
    op.execute("""
        ALTER TABLE timer_cards DROP CONSTRAINT IF EXISTS fk_timer_cards_factory
    """)
