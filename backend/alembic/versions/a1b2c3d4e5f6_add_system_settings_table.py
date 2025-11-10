"""add_system_settings_table

Revision ID: a1b2c3d4e5f6
Revises: 5584c9c895e2
Create Date: 2025-10-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5584c9c895e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create system_settings table"""
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)

    # Only create table if it doesn't exist
    if 'system_settings' not in inspector.get_table_names():
        op.create_table(
            'system_settings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('key', sa.String(length=100), nullable=False),
            sa.Column('value', sa.String(length=255), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_system_settings_id'), 'system_settings', ['id'], unique=False)
        op.create_index(op.f('ix_system_settings_key'), 'system_settings', ['key'], unique=True)

        # Insert default visibility setting
        op.execute(
            """
            INSERT INTO system_settings (key, value, description)
            VALUES ('content_visibility_enabled', 'true', 'Controls visibility of content for ADMIN and KANRINSHA users')
            """
        )


def downgrade() -> None:
    """Drop system_settings table"""
    op.drop_index(op.f('ix_system_settings_key'), table_name='system_settings')
    op.drop_index(op.f('ix_system_settings_id'), table_name='system_settings')
    op.drop_table('system_settings')
