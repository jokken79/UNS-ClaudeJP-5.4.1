"""Add search indexes for better performance

Revision ID: add_search_indexes
Revises: 001
Create Date: 2025-11-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_search_indexes'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add pg_trgm extension for fuzzy text search
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Indexes for candidates table

    # Trigram indexes for fuzzy search on names
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_candidate_name_kanji_trgm
        ON candidates USING gin (full_name_kanji gin_trgm_ops)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_candidate_name_kana_trgm
        ON candidates USING gin (full_name_kana gin_trgm_ops)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_candidate_name_roman_trgm
        ON candidates USING gin (full_name_roman gin_trgm_ops)
    """)

    # Regular B-tree index for rirekisho_id search (already exists, but ensure)
    op.create_index(
        'idx_candidate_rirekisho_id',
        'candidates',
        ['rirekisho_id'],
        unique=False,
        postgresql_if_not_exists=True
    )

    # Index for status filtering (excluding deleted)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_candidate_status_active
        ON candidates(status)
        WHERE deleted_at IS NULL
    """)

    # Index for date of birth (for age calculations and filtering)
    op.create_index(
        'idx_candidate_date_of_birth',
        'candidates',
        ['date_of_birth'],
        unique=False,
        postgresql_if_not_exists=True
    )

    # Index for email (for duplicate checking)
    op.create_index(
        'idx_candidate_email',
        'candidates',
        ['email'],
        unique=False,
        postgresql_if_not_exists=True
    )

    # Composite index for duplicate detection (name + birthdate)
    op.create_index(
        'idx_candidate_name_birthdate',
        'candidates',
        ['full_name_kanji', 'date_of_birth'],
        unique=False,
        postgresql_if_not_exists=True
    )

    # Indexes for employees table

    # Trigram index for employee name search
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_employee_name_kanji_trgm
        ON employees USING gin (full_name_kanji gin_trgm_ops)
    """)

    # Index for rirekisho_id (for relationship lookups)
    op.create_index(
        'idx_employee_rirekisho_id',
        'employees',
        ['rirekisho_id'],
        unique=False,
        postgresql_if_not_exists=True
    )

    # Index for factory_id (for filtering by factory)
    op.create_index(
        'idx_employee_factory_id',
        'employees',
        ['factory_id'],
        unique=False,
        postgresql_if_not_exists=True
    )

    # Index for hakenmoto_id (employee number)
    op.create_index(
        'idx_employee_hakenmoto_id',
        'employees',
        ['hakenmoto_id'],
        unique=True,
        postgresql_if_not_exists=True
    )


def downgrade():
    # Drop all created indexes
    op.execute("DROP INDEX IF EXISTS idx_candidate_name_kanji_trgm")
    op.execute("DROP INDEX IF EXISTS idx_candidate_name_kana_trgm")
    op.execute("DROP INDEX IF EXISTS idx_candidate_name_roman_trgm")
    op.drop_index('idx_candidate_rirekisho_id', table_name='candidates', if_exists=True)
    op.execute("DROP INDEX IF EXISTS idx_candidate_status_active")
    op.drop_index('idx_candidate_date_of_birth', table_name='candidates', if_exists=True)
    op.drop_index('idx_candidate_email', table_name='candidates', if_exists=True)
    op.drop_index('idx_candidate_name_birthdate', table_name='candidates', if_exists=True)

    op.execute("DROP INDEX IF EXISTS idx_employee_name_kanji_trgm")
    op.drop_index('idx_employee_rirekisho_id', table_name='employees', if_exists=True)
    op.drop_index('idx_employee_factory_id', table_name='employees', if_exists=True)
    op.drop_index('idx_employee_hakenmoto_id', table_name='employees', if_exists=True)

    # Note: We don't drop pg_trgm extension as other migrations might use it
