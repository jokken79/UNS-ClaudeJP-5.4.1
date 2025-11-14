"""merge_all_heads_2025_11_07

Revision ID: 7fe49ba2ab7c
Revises: 2025_11_06_refresh_tokens, 2025_11_06_soft_del_rem, b6dc75dfbe7c
Create Date: 2025-11-07 16:08:18.056288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fe49ba2ab7c'
down_revision: Union[str, None] = ('2025_11_06_refresh_tokens', '2025_11_06_soft_del_rem', 'b6dc75dfbe7c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
