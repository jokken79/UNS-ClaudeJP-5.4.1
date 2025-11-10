"""add_refresh_tokens_table

Revision ID: 2025_11_06_refresh_tokens
Revises:
Create Date: 2025-11-06

Add refresh_tokens table for JWT refresh token rotation.
This enables secure token refresh without exposing access tokens.

Security features:
- Token rotation on each refresh
- Revocation support
- Device/IP tracking for audit trail
- Automatic cleanup of expired tokens
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025_11_06_refresh_tokens'
down_revision = 'a1b2c3d4e5f6'  # Latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Create refresh_tokens table"""
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('revoked', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_expires_at'), 'refresh_tokens', ['expires_at'], unique=False)

    # Index for cleanup queries (find expired + revoked tokens)
    op.create_index(
        'ix_refresh_tokens_cleanup',
        'refresh_tokens',
        ['expires_at', 'revoked'],
        unique=False
    )


def downgrade():
    """Drop refresh_tokens table"""
    op.drop_index('ix_refresh_tokens_cleanup', table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_expires_at'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
