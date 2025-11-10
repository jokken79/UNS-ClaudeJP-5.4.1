"""hybrid bd proposal - add smart columns and triggers

Revision ID: 2025_10_27_007
Revises: 2025_10_27_006
Create Date: 2025-10-27

This migration implements the hybrid database proposal by adding smart columns
and database triggers to automatically maintain employee status and visa alerts.

New Features:
- current_status column with automatic sync to is_active
- visa_renewal_alert flag with automatic calculation
- visa_alert_days configurable threshold (default 30 days)
- Database triggers for automatic status synchronization

Estimated execution time: 2-3 minutes
Impact: Automated status management, proactive visa alerts
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_10_27_007'
down_revision: str | None = '2025_10_27_006'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    """Add hybrid BD proposal columns and triggers"""

    # Add new columns to employees table
    op.execute("""
        ALTER TABLE employees
        ADD COLUMN IF NOT EXISTS current_status VARCHAR(20) DEFAULT 'active',
        ADD COLUMN IF NOT EXISTS visa_renewal_alert BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS visa_alert_days INTEGER DEFAULT 30
    """)

    # Update current_status based on existing is_active and termination_date
    op.execute("""
        UPDATE employees
        SET current_status = CASE
            WHEN is_active = FALSE AND termination_date IS NOT NULL THEN 'terminated'
            WHEN is_active = TRUE THEN 'active'
            ELSE 'active'
        END
    """)

    # Create trigger function to sync current_status with is_active
    op.execute("""
        CREATE OR REPLACE FUNCTION sync_employee_status()
        RETURNS TRIGGER AS $$
        BEGIN
            -- When current_status is set to 'terminated', set is_active to FALSE
            IF NEW.current_status = 'terminated' AND NEW.termination_date IS NOT NULL THEN
                NEW.is_active = FALSE;
            END IF;

            -- When current_status is set to 'active', set is_active to TRUE and clear termination_date
            IF NEW.current_status = 'active' THEN
                NEW.is_active = TRUE;
                NEW.termination_date = NULL;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to execute sync function on insert/update
    op.execute("""
        DROP TRIGGER IF EXISTS employee_status_sync ON employees;
        CREATE TRIGGER employee_status_sync
            BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW
            EXECUTE FUNCTION sync_employee_status();
    """)

    # Create trigger function to check visa expiration
    op.execute("""
        CREATE OR REPLACE FUNCTION check_visa_expiration()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Only check if zairyu_expire_date is set
            IF NEW.zairyu_expire_date IS NOT NULL THEN
                -- Calculate days until expiration
                IF NEW.zairyu_expire_date - CURRENT_DATE <= NEW.visa_alert_days THEN
                    NEW.visa_renewal_alert = TRUE;
                ELSE
                    NEW.visa_renewal_alert = FALSE;
                END IF;
            ELSE
                -- No visa date set, no alert
                NEW.visa_renewal_alert = FALSE;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to execute visa check on insert/update
    op.execute("""
        DROP TRIGGER IF EXISTS visa_expiration_check ON employees;
        CREATE TRIGGER visa_expiration_check
            BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW
            EXECUTE FUNCTION check_visa_expiration();
    """)

    # Update existing records to calculate visa_renewal_alert
    op.execute("""
        UPDATE employees
        SET visa_renewal_alert = CASE
            WHEN zairyu_expire_date IS NOT NULL AND
                 zairyu_expire_date - CURRENT_DATE <= visa_alert_days THEN TRUE
            ELSE FALSE
        END
    """)

    # Add index for efficient visa alert queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_employees_visa_alert
        ON employees(visa_renewal_alert, zairyu_expire_date)
        WHERE visa_renewal_alert = TRUE
    """)

    # Add index for current_status queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_employees_current_status
        ON employees(current_status)
    """)


def downgrade():
    """Remove hybrid BD proposal columns and triggers"""

    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS employee_status_sync ON employees")
    op.execute("DROP TRIGGER IF EXISTS visa_expiration_check ON employees")

    # Drop trigger functions
    op.execute("DROP FUNCTION IF EXISTS sync_employee_status()")
    op.execute("DROP FUNCTION IF EXISTS check_visa_expiration()")

    # Drop indexes
    op.drop_index('idx_employees_visa_alert', table_name='employees', if_exists=True)
    op.drop_index('idx_employees_current_status', table_name='employees', if_exists=True)

    # Remove columns
    op.execute("""
        ALTER TABLE employees
        DROP COLUMN IF EXISTS current_status,
        DROP COLUMN IF EXISTS visa_renewal_alert,
        DROP COLUMN IF EXISTS visa_alert_days
    """)
