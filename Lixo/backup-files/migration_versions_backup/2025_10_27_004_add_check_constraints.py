"""add check constraints for data validation

Revision ID: 2025_10_27_004
Revises: 2025_10_27_003
Create Date: 2025-10-27

This migration adds CHECK constraints to enforce data validation rules at the
database level. This prevents invalid data from being inserted or updated.

Estimated execution time: 3-4 minutes
Impact: Enforces data integrity, prevents invalid data
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_10_27_004'
down_revision: str | None = '2025_10_27_003'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    """Add CHECK constraints for data validation"""

    # Users constraints - email format validation
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT IF NOT EXISTS chk_users_email_format
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    """)

    # Apartments constraints
    op.execute("""
        ALTER TABLE apartments ADD CONSTRAINT IF NOT EXISTS chk_apartments_rent_positive
        CHECK (monthly_rent > 0)
    """)
    op.execute("""
        ALTER TABLE apartments ADD CONSTRAINT IF NOT EXISTS chk_apartments_capacity_positive
        CHECK (capacity > 0)
    """)

    # Employees constraints - hourly rate must be non-negative
    op.execute("""
        ALTER TABLE employees ADD CONSTRAINT IF NOT EXISTS chk_employees_jikyu_positive
        CHECK (jikyu >= 0)
    """)

    # Timer Cards constraints - clock times must be paired
    op.execute("""
        ALTER TABLE timer_cards ADD CONSTRAINT IF NOT EXISTS chk_timer_cards_clock_times
        CHECK ((clock_in IS NULL AND clock_out IS NULL) OR (clock_in IS NOT NULL AND clock_out IS NOT NULL))
    """)

    # Timer Cards constraints - hours must be non-negative
    op.execute("""
        ALTER TABLE timer_cards ADD CONSTRAINT IF NOT EXISTS chk_timer_cards_hours_positive
        CHECK (regular_hours >= 0 AND overtime_hours >= 0 AND night_hours >= 0 AND holiday_hours >= 0)
    """)

    # Timer Cards constraints - total hours can't exceed 24 in a day
    op.execute("""
        ALTER TABLE timer_cards ADD CONSTRAINT IF NOT EXISTS chk_timer_cards_hours_total
        CHECK (regular_hours + overtime_hours + night_hours + holiday_hours <= 24)
    """)

    # Salary Calculations constraints - valid month range
    op.execute("""
        ALTER TABLE salary_calculations ADD CONSTRAINT IF NOT EXISTS chk_salary_month
        CHECK (month >= 1 AND month <= 12)
    """)

    # Salary Calculations constraints - reasonable year range
    op.execute("""
        ALTER TABLE salary_calculations ADD CONSTRAINT IF NOT EXISTS chk_salary_year
        CHECK (year >= 2000 AND year <= 2100)
    """)

    # Requests constraints - end date must be after start date
    op.execute("""
        ALTER TABLE requests ADD CONSTRAINT IF NOT EXISTS chk_requests_date_range
        CHECK (end_date >= start_date)
    """)

    # Contracts constraints - end date must be after start date (if set)
    op.execute("""
        ALTER TABLE contracts ADD CONSTRAINT IF NOT EXISTS chk_contracts_date_range
        CHECK (end_date IS NULL OR end_date >= start_date)
    """)

    # Documents constraints - must belong to either candidate OR employee
    op.execute("""
        ALTER TABLE documents ADD CONSTRAINT IF NOT EXISTS chk_documents_owner
        CHECK ((candidate_id IS NOT NULL AND employee_id IS NULL) OR (candidate_id IS NULL AND employee_id IS NOT NULL))
    """)

    # Documents constraints - file size limits (max 50MB)
    op.execute("""
        ALTER TABLE documents ADD CONSTRAINT IF NOT EXISTS chk_documents_file_size
        CHECK (file_size > 0 AND file_size < 52428800)
    """)


def downgrade():
    """Remove CHECK constraints"""

    # Drop all constraints created in upgrade()
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_users_email_format")
    op.execute("ALTER TABLE apartments DROP CONSTRAINT IF EXISTS chk_apartments_rent_positive")
    op.execute("ALTER TABLE apartments DROP CONSTRAINT IF EXISTS chk_apartments_capacity_positive")
    op.execute("ALTER TABLE employees DROP CONSTRAINT IF EXISTS chk_employees_jikyu_positive")
    op.execute("ALTER TABLE timer_cards DROP CONSTRAINT IF EXISTS chk_timer_cards_clock_times")
    op.execute("ALTER TABLE timer_cards DROP CONSTRAINT IF EXISTS chk_timer_cards_hours_positive")
    op.execute("ALTER TABLE timer_cards DROP CONSTRAINT IF EXISTS chk_timer_cards_hours_total")
    op.execute("ALTER TABLE salary_calculations DROP CONSTRAINT IF EXISTS chk_salary_month")
    op.execute("ALTER TABLE salary_calculations DROP CONSTRAINT IF EXISTS chk_salary_year")
    op.execute("ALTER TABLE requests DROP CONSTRAINT IF EXISTS chk_requests_date_range")
    op.execute("ALTER TABLE contracts DROP CONSTRAINT IF EXISTS chk_contracts_date_range")
    op.execute("ALTER TABLE documents DROP CONSTRAINT IF EXISTS chk_documents_owner")
    op.execute("ALTER TABLE documents DROP CONSTRAINT IF EXISTS chk_documents_file_size")
