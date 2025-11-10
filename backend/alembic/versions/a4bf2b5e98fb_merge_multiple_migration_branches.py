"""Merge multiple migration branches

Revision ID: a4bf2b5e98fb
Revises: 2025_10_27_007, 001, page_visibility_001
Create Date: 2025-11-04 17:39:07.456165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4bf2b5e98fb'
down_revision: Union[str, None] = ('2025_10_27_007', '001', 'page_visibility_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
