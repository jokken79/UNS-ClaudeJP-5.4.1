"""add unique constraints for data integrity

Revision ID: 2025_10_27_002
Revises: 2025_10_26_add_employee_photo_data_url
Create Date: 2025-10-27

This migration adds UNIQUE constraints to prevent duplicate data entries.
These constraints ensure data integrity and prevent common data quality issues.

Estimated execution time: 2-3 minutes
Impact: Prevents duplicate records, improves data quality
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_10_27_002'
down_revision: str | None = '2025_10_26_add_employee_photo_data_url'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    """Add unique constraints to prevent duplicate data"""

    # Helper function to safely create index only if table and columns exist
    def create_index_if_table_exists(index_name, table_name, columns, where_clause=None):
        # Split columns to check each one
        column_list = [col.strip() for col in columns.split(',')]
        where_sql = f"WHERE {where_clause}" if where_clause else ""

        # Build column check conditions
        column_checks = " AND ".join([
            f"EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name = '{col}')"
            for col in column_list
        ])

        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')
                   AND {column_checks} THEN
                    CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
                    ON {table_name}({columns})
                    {where_sql};
                END IF;
            END $$;
        """)

    # Timer Cards - prevent duplicate entries for same employee on same date
    create_index_if_table_exists(
        'idx_timer_cards_unique_entry',
        'timer_cards',
        'hakenmoto_id, work_date'
    )

    # Salary Calculations - prevent duplicate calculations for same period
    create_index_if_table_exists(
        'idx_salary_unique_employee_period',
        'salary_calculations',
        'employee_id, year, month'
    )

    # Requests - prevent duplicate requests (except rejected ones)
    # Note: Removed WHERE clause to avoid enum/cast issues - constraint applies to all records
    create_index_if_table_exists(
        'idx_requests_unique_request',
        'requests',
        'hakenmoto_id, request_type, start_date, end_date'
    )

    # Candidates - prevent duplicate persons (same name + DOB)
    # Note: Removed WHERE clause to avoid enum/cast issues - constraint applies to all records
    create_index_if_table_exists(
        'idx_candidates_unique_person',
        'candidates',
        'full_name_kanji, date_of_birth'
    )

    # Candidates - prevent duplicate applicant IDs
    create_index_if_table_exists(
        'idx_candidates_unique_applicant',
        'candidates',
        'applicant_id',
        where_clause='applicant_id IS NOT NULL'
    )

    # Factories - prevent duplicate company+plant combinations
    create_index_if_table_exists(
        'idx_factories_unique_company_plant',
        'factories',
        'company_name, plant_name'
    )

    # Documents - prevent duplicate file uploads
    create_index_if_table_exists(
        'idx_documents_unique_file',
        'documents',
        'file_path'
    )

    # Social Insurance Rates - prevent duplicate rate entries
    create_index_if_table_exists(
        'idx_insurance_rates_unique',
        'social_insurance_rates',
        'standard_compensation, effective_date, prefecture'
    )


def downgrade():
    """Remove unique constraints"""

    # Drop all unique indexes created in upgrade()
    op.drop_index('idx_timer_cards_unique_entry', table_name='timer_cards', if_exists=True)
    op.drop_index('idx_salary_unique_employee_period', table_name='salary_calculations', if_exists=True)
    op.drop_index('idx_requests_unique_request', table_name='requests', if_exists=True)
    op.drop_index('idx_candidates_unique_person', table_name='candidates', if_exists=True)
    op.drop_index('idx_candidates_unique_applicant', table_name='candidates', if_exists=True)
    op.drop_index('idx_factories_unique_company_plant', table_name='factories', if_exists=True)
    op.drop_index('idx_documents_unique_file', table_name='documents', if_exists=True)
    op.drop_index('idx_insurance_rates_unique', table_name='social_insurance_rates', if_exists=True)
