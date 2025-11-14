"""add_physical_and_family_dependent_columns

Revision ID: b6dc75dfbe7c
Revises: a4bf2b5e98fb
Create Date: 2025-11-06 06:22:43.703240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


# revision identifiers, used by Alembic.
revision: str = 'b6dc75dfbe7c'
down_revision: Union[str, None] = 'a4bf2b5e98fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add family dependent columns (扶養 - Dependent status for each family member)
    if not _column_exists('candidates', 'family_dependent_1'):
        op.add_column('candidates', sa.Column('family_dependent_1', sa.String(length=50), nullable=True))
    if not _column_exists('candidates', 'family_dependent_2'):
        op.add_column('candidates', sa.Column('family_dependent_2', sa.String(length=50), nullable=True))
    if not _column_exists('candidates', 'family_dependent_3'):
        op.add_column('candidates', sa.Column('family_dependent_3', sa.String(length=50), nullable=True))
    if not _column_exists('candidates', 'family_dependent_4'):
        op.add_column('candidates', sa.Column('family_dependent_4', sa.String(length=50), nullable=True))
    if not _column_exists('candidates', 'family_dependent_5'):
        op.add_column('candidates', sa.Column('family_dependent_5', sa.String(length=50), nullable=True))

    # Add physical information columns
    if not _column_exists('candidates', 'height'):
        op.add_column('candidates', sa.Column('height', sa.Float(), nullable=True))  # 身長(cm)
    if not _column_exists('candidates', 'weight'):
        op.add_column('candidates', sa.Column('weight', sa.Float(), nullable=True))  # 体重(kg)
    if not _column_exists('candidates', 'clothing_size'):
        op.add_column('candidates', sa.Column('clothing_size', sa.String(length=10), nullable=True))  # 服のサイズ
    if not _column_exists('candidates', 'waist'):
        op.add_column('candidates', sa.Column('waist', sa.Integer(), nullable=True))  # ウエスト(cm)
    if not _column_exists('candidates', 'shoe_size'):
        op.add_column('candidates', sa.Column('shoe_size', sa.Float(), nullable=True))  # 靴サイズ(cm)

    # Add vision columns
    if not _column_exists('candidates', 'vision_right'):
        op.add_column('candidates', sa.Column('vision_right', sa.Float(), nullable=True))  # 視力(右)
    if not _column_exists('candidates', 'vision_left'):
        op.add_column('candidates', sa.Column('vision_left', sa.Float(), nullable=True))  # 視力(左)


def downgrade() -> None:
    # Remove columns in reverse order
    if _column_exists('candidates', 'vision_left'):
        op.drop_column('candidates', 'vision_left')
    if _column_exists('candidates', 'vision_right'):
        op.drop_column('candidates', 'vision_right')

    if _column_exists('candidates', 'shoe_size'):
        op.drop_column('candidates', 'shoe_size')
    if _column_exists('candidates', 'waist'):
        op.drop_column('candidates', 'waist')
    if _column_exists('candidates', 'clothing_size'):
        op.drop_column('candidates', 'clothing_size')
    if _column_exists('candidates', 'weight'):
        op.drop_column('candidates', 'weight')
    if _column_exists('candidates', 'height'):
        op.drop_column('candidates', 'height')

    if _column_exists('candidates', 'family_dependent_5'):
        op.drop_column('candidates', 'family_dependent_5')
    if _column_exists('candidates', 'family_dependent_4'):
        op.drop_column('candidates', 'family_dependent_4')
    if _column_exists('candidates', 'family_dependent_3'):
        op.drop_column('candidates', 'family_dependent_3')
    if _column_exists('candidates', 'family_dependent_2'):
        op.drop_column('candidates', 'family_dependent_2')
    if _column_exists('candidates', 'family_dependent_1'):
        op.drop_column('candidates', 'family_dependent_1')
