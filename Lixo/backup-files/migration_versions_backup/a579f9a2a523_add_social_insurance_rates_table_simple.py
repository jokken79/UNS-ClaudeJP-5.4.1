"""add_social_insurance_rates_table_simple

Revision ID: a579f9a2a523
Revises: fe6aac62e522
Create Date: 2025-10-24 04:30:02.270121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a579f9a2a523'
down_revision: Union[str, None] = 'fe6aac62e522'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create social_insurance_rates table (idempotent - skip if exists)
    from sqlalchemy import inspect

    bind = op.get_bind()
    inspector = inspect(bind)

    # Check if table already exists (created by initial_baseline via create_all)
    if 'social_insurance_rates' not in inspector.get_table_names():
        op.create_table(
            'social_insurance_rates',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('min_compensation', sa.Integer(), nullable=False),
            sa.Column('max_compensation', sa.Integer(), nullable=False),
            sa.Column('standard_compensation', sa.Integer(), nullable=False),
            sa.Column('health_insurance_total', sa.Integer(), nullable=True),
            sa.Column('health_insurance_employee', sa.Integer(), nullable=True),
            sa.Column('health_insurance_employer', sa.Integer(), nullable=True),
            sa.Column('nursing_insurance_total', sa.Integer(), nullable=True),
            sa.Column('nursing_insurance_employee', sa.Integer(), nullable=True),
            sa.Column('nursing_insurance_employer', sa.Integer(), nullable=True),
            sa.Column('pension_insurance_total', sa.Integer(), nullable=True),
            sa.Column('pension_insurance_employee', sa.Integer(), nullable=True),
            sa.Column('pension_insurance_employer', sa.Integer(), nullable=True),
            sa.Column('effective_date', sa.Date(), nullable=False),
            sa.Column('prefecture', sa.String(length=20), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_social_insurance_rates_id'), 'social_insurance_rates', ['id'], unique=False)


def downgrade() -> None:
    # Drop social_insurance_rates table
    op.drop_index(op.f('ix_social_insurance_rates_id'), table_name='social_insurance_rates')
    op.drop_table('social_insurance_rates')
