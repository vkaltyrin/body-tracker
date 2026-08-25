"""Исходная таблица дней

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "training_day",
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column("yoga", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("gym", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("note", sa.String(), nullable=False, server_default=sa.text("''")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("training_day")
