"""add company plant separation

Revision ID: ab12cd34ef56
Revises: fe6aac62e522
Create Date: 2025-10-25 11:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


# revision identifiers, used by Alembic.
revision: str = 'ab12cd34ef56'
down_revision: str | None = 'a1b2c3d4e5f6'
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    # Drop view that depends on factory_id column (will recreate later)
    op.execute("DROP VIEW IF EXISTS vw_employees_with_age")

    # Increase factory_id column size for all tables
    # PostgreSQL needs explicit type casting

    # Factories table
    op.alter_column('factories', 'factory_id',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=200),
               existing_nullable=False)

    if not _column_exists('factories', 'company_name'):
        op.add_column('factories', sa.Column('company_name', sa.String(length=100), nullable=True))
    if not _column_exists('factories', 'plant_name'):
        op.add_column('factories', sa.Column('plant_name', sa.String(length=100), nullable=True))

    # Employees table
    op.alter_column('employees', 'factory_id',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=200),
               existing_nullable=True)

    if not _column_exists('employees', 'company_name'):
        op.add_column('employees', sa.Column('company_name', sa.String(length=100), nullable=True))
    if not _column_exists('employees', 'plant_name'):
        op.add_column('employees', sa.Column('plant_name', sa.String(length=100), nullable=True))

    # Contract workers table
    op.alter_column('contract_workers', 'factory_id',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=200),
               existing_nullable=True)

    if not _column_exists('contract_workers', 'company_name'):
        op.add_column('contract_workers', sa.Column('company_name', sa.String(length=100), nullable=True))
    if not _column_exists('contract_workers', 'plant_name'):
        op.add_column('contract_workers', sa.Column('plant_name', sa.String(length=100), nullable=True))

    # Update existing data: Split factory_id into company_name and plant_name
    # Format expected: Company_Plant or Company__Plant
    op.execute("""
        UPDATE factories
        SET
            company_name = split_part(factory_id, '_', 1),
            plant_name = CASE
                WHEN factory_id LIKE '%__%' THEN split_part(factory_id, '__', 2)
                WHEN factory_id LIKE '%_%' THEN split_part(factory_id, '_', 2)
                ELSE ''
            END
        WHERE factory_id IS NOT NULL
    """)

    op.execute("""
        UPDATE employees
        SET
            company_name = split_part(factory_id, '_', 1),
            plant_name = CASE
                WHEN factory_id LIKE '%__%' THEN split_part(factory_id, '__', 2)
                WHEN factory_id LIKE '%_%' THEN split_part(factory_id, '_', 2)
                ELSE ''
            END
        WHERE factory_id IS NOT NULL
    """)

    op.execute("""
        UPDATE contract_workers
        SET
            company_name = split_part(factory_id, '_', 1),
            plant_name = CASE
                WHEN factory_id LIKE '%__%' THEN split_part(factory_id, '__', 2)
                WHEN factory_id LIKE '%_%' THEN split_part(factory_id, '_', 2)
                ELSE ''
            END
        WHERE factory_id IS NOT NULL
    """)

    # Recreate the view that was dropped earlier
    op.execute("""
        CREATE OR REPLACE VIEW vw_employees_with_age AS
        SELECT
            e.*,
            EXTRACT(YEAR FROM AGE(e.date_of_birth)) AS calculated_age,
            CASE
                WHEN e.zairyu_expire_date - CURRENT_DATE <= e.visa_alert_days THEN TRUE
                ELSE FALSE
            END AS visa_expiring_soon,
            e.zairyu_expire_date - CURRENT_DATE AS days_until_visa_expiration,
            f.name AS factory_name
        FROM employees e
        LEFT JOIN factories f ON e.factory_id = f.factory_id;
    """)


def downgrade():
    # Drop view before altering columns
    op.execute("DROP VIEW IF EXISTS vw_employees_with_age")

    # Remove new columns
    if _column_exists('contract_workers', 'plant_name'):
        op.drop_column('contract_workers', 'plant_name')
    if _column_exists('contract_workers', 'company_name'):
        op.drop_column('contract_workers', 'company_name')
    if _column_exists('employees', 'plant_name'):
        op.drop_column('employees', 'plant_name')
    if _column_exists('employees', 'company_name'):
        op.drop_column('employees', 'company_name')
    if _column_exists('factories', 'plant_name'):
        op.drop_column('factories', 'plant_name')
    if _column_exists('factories', 'company_name'):
        op.drop_column('factories', 'company_name')

    # Restore factory_id column size
    op.alter_column('contract_workers', 'factory_id',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.String(length=20),
               existing_nullable=True)

    op.alter_column('employees', 'factory_id',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.String(length=20),
               existing_nullable=True)

    op.alter_column('factories', 'factory_id',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.String(length=20),
               existing_nullable=False)

    # Recreate the view with original column sizes
    op.execute("""
        CREATE OR REPLACE VIEW vw_employees_with_age AS
        SELECT
            e.*,
            EXTRACT(YEAR FROM AGE(e.date_of_birth)) AS calculated_age,
            CASE
                WHEN e.zairyu_expire_date - CURRENT_DATE <= e.visa_alert_days THEN TRUE
                ELSE FALSE
            END AS visa_expiring_soon,
            e.zairyu_expire_date - CURRENT_DATE AS days_until_visa_expiration,
            f.name AS factory_name
        FROM employees e
        LEFT JOIN factories f ON e.factory_id = f.factory_id;
    """)
