"""add custom ai provider

Revision ID: 9a7e4d2c1f11
Revises: b2b2e541b0cd
Create Date: 2026-05-05 04:20:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9a7e4d2c1f11"
down_revision: Union[str, None] = "b2b2e541b0cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE aiprovider ADD VALUE IF NOT EXISTS 'CUSTOM'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values safely in-place.
    pass
