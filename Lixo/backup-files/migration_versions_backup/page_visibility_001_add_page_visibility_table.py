"""add_page_visibility_table

Revision ID: page_visibility_001
Revises: a1b2c3d4e5f6
Create Date: 2025-11-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'page_visibility_001'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create page_visibility table
    op.create_table(
        'page_visibility',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('page_key', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('page_name', sa.String(100), nullable=False),
        sa.Column('page_name_en', sa.String(100), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), default=True, nullable=False),
        sa.Column('path', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('disabled_message', sa.String(255), nullable=True),
        sa.Column('last_toggled_by', sa.Integer(), nullable=True),
        sa.Column('last_toggled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['last_toggled_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('page_visibility')
