"""store the account that sent the contact email

Revision ID: c3d91a7e4b20
Revises: b7c2e4a91d10
Create Date: 2026-10-20 18:16:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3d91a7e4b20"
down_revision: str | Sequence[str] | None = "b7c2e4a91d10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("sent_from", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("leads", "sent_from")
