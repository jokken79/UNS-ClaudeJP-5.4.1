"""Add NYUUSHA 入社連絡票 (New Hire Notification Form) fields to requests table

This migration adds:
1. candidate_id: Foreign key linking request to candidate
2. employee_data: JSONB field storing employee-specific data before employee creation

Revision ID: 003
Revises: 001
Create Date: 2025-11-13 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add NYUUSHA workflow fields to requests table"""

    # Add candidate_id column (FK to candidates table)
    op.add_column(
        'requests',
        sa.Column('candidate_id', sa.Integer(), nullable=True)
    )

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_requests_candidate_id',
        'requests',
        'candidates',
        ['candidate_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Create index for faster queries
    op.create_index(
        'idx_requests_candidate_id',
        'requests',
        ['candidate_id'],
        unique=False
    )

    # Add employee_data column (JSONB for flexible employee data)
    # JSONB is used for PostgreSQL JSON support with indexing capabilities
    op.add_column(
        'requests',
        sa.Column(
            'employee_data',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment='Flexible JSON storage for employee-specific data (factory_id, hire_date, jikyu, position, etc.)'
        )
    )

    # Create GIN index on JSONB column for efficient JSON queries
    op.execute(
        'CREATE INDEX idx_requests_employee_data ON requests USING GIN (employee_data)'
    )


def downgrade() -> None:
    """Remove NYUUSHA workflow fields from requests table"""

    # Drop GIN index on JSONB
    op.drop_index('idx_requests_employee_data', table_name='requests')

    # Drop employee_data column
    op.drop_column('requests', 'employee_data')

    # Drop candidate_id FK and index
    op.drop_index('idx_requests_candidate_id', table_name='requests')
    op.drop_constraint('fk_requests_candidate_id', 'requests', type_='foreignkey')
    op.drop_column('requests', 'candidate_id')
