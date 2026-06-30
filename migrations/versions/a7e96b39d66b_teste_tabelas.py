"""teste_tabelas

Revision ID: a7e96b39d66b
Revises: e9bbb9543f91
Create Date: 2026-06-30 17:05:16.516870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7e96b39d66b'
down_revision: Union[str, Sequence[str], None] = 'e9bbb9543f91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
