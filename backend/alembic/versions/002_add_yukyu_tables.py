"""Add yukyu tables (balances, requests, usage_details)

Revision ID: 002
Revises: 001
Create Date: 2025-11-11 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create yukyu-related tables"""

    # Create yukyu_status enum
    yukyu_status_enum = postgresql.ENUM('ACTIVE', 'EXPIRED', name='yukyu_status', create_type=True)
    yukyu_status_enum.create(op.get_bind(), checkfirst=True)

    # Create yukyu_balances table
    op.create_table(
        'yukyu_balances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('assigned_date', sa.Date(), nullable=False),
        sa.Column('months_worked', sa.Integer(), nullable=False),
        sa.Column('days_assigned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_carried_over', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_remaining', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_expired', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_available', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_on', sa.Date(), nullable=False),
        sa.Column('status', yukyu_status_enum, nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_yukyu_balances_id'), 'yukyu_balances', ['id'], unique=False)
    op.create_index(op.f('ix_yukyu_balances_employee_id'), 'yukyu_balances', ['employee_id'], unique=False)
    op.create_index(op.f('ix_yukyu_balances_fiscal_year'), 'yukyu_balances', ['fiscal_year'], unique=False)

    # Create yukyu_requests table
    op.create_table(
        'yukyu_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('requested_by_user_id', sa.Integer(), nullable=False),
        sa.Column('factory_id', sa.Integer(), nullable=True),
        sa.Column('request_type', sa.Enum('yukyu', 'hankyu', 'ikkikokoku', 'taisha', name='request_type'), nullable=False, server_default='yukyu'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('days_requested', sa.Numeric(precision=4, scale=1), nullable=False),
        sa.Column('yukyu_available_at_request', sa.Integer(), nullable=False),
        sa.Column('request_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='request_status'), nullable=False, server_default='pending'),
        sa.Column('approved_by_user_id', sa.Integer(), nullable=True),
        sa.Column('approval_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requested_by_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['factory_id'], ['factories.id'])
    )
    op.create_index(op.f('ix_yukyu_requests_id'), 'yukyu_requests', ['id'], unique=False)
    op.create_index(op.f('ix_yukyu_requests_employee_id'), 'yukyu_requests', ['employee_id'], unique=False)
    op.create_index(op.f('ix_yukyu_requests_factory_id'), 'yukyu_requests', ['factory_id'], unique=False)
    op.create_index(op.f('ix_yukyu_requests_status'), 'yukyu_requests', ['status'], unique=False)

    # Create yukyu_usage_details table
    op.create_table(
        'yukyu_usage_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=False),
        sa.Column('balance_id', sa.Integer(), nullable=False),
        sa.Column('usage_date', sa.Date(), nullable=False),
        sa.Column('days_deducted', sa.Numeric(precision=3, scale=1), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['request_id'], ['yukyu_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['balance_id'], ['yukyu_balances.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_yukyu_usage_details_id'), 'yukyu_usage_details', ['id'], unique=False)
    op.create_index(op.f('ix_yukyu_usage_details_request_id'), 'yukyu_usage_details', ['request_id'], unique=False)
    op.create_index(op.f('ix_yukyu_usage_details_balance_id'), 'yukyu_usage_details', ['balance_id'], unique=False)
    op.create_index(op.f('ix_yukyu_usage_details_usage_date'), 'yukyu_usage_details', ['usage_date'], unique=False)


def downgrade() -> None:
    """Drop yukyu-related tables"""
    op.drop_index(op.f('ix_yukyu_usage_details_usage_date'), table_name='yukyu_usage_details')
    op.drop_index(op.f('ix_yukyu_usage_details_balance_id'), table_name='yukyu_usage_details')
    op.drop_index(op.f('ix_yukyu_usage_details_request_id'), table_name='yukyu_usage_details')
    op.drop_index(op.f('ix_yukyu_usage_details_id'), table_name='yukyu_usage_details')
    op.drop_table('yukyu_usage_details')

    op.drop_index(op.f('ix_yukyu_requests_status'), table_name='yukyu_requests')
    op.drop_index(op.f('ix_yukyu_requests_factory_id'), table_name='yukyu_requests')
    op.drop_index(op.f('ix_yukyu_requests_employee_id'), table_name='yukyu_requests')
    op.drop_index(op.f('ix_yukyu_requests_id'), table_name='yukyu_requests')
    op.drop_table('yukyu_requests')

    op.drop_index(op.f('ix_yukyu_balances_fiscal_year'), table_name='yukyu_balances')
    op.drop_index(op.f('ix_yukyu_balances_employee_id'), table_name='yukyu_balances')
    op.drop_index(op.f('ix_yukyu_balances_id'), table_name='yukyu_balances')
    op.drop_table('yukyu_balances')

    # Drop enum
    yukyu_status_enum = postgresql.ENUM('ACTIVE', 'EXPIRED', name='yukyu_status')
    yukyu_status_enum.drop(op.get_bind(), checkfirst=True)
