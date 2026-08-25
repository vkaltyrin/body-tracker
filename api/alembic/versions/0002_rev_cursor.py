"""Курсор дельта-синхронизации

Ревизия — монотонный счётчик сервера. Клиент хранит последнюю виденную и просит
всё, что больше: так синхронизация не зависит от часов и часовых поясов.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS training_day_rev_seq")
    op.add_column("training_day", sa.Column("rev", sa.BigInteger(), nullable=True))
    # Существующим строкам раздаём ревизии в порядке дат — так первый клиент
    # получит их одной последовательной пачкой.
    op.execute(
        """
        UPDATE training_day SET rev = seq.n
          FROM (SELECT day, nextval('training_day_rev_seq') AS n
                  FROM (SELECT day FROM training_day ORDER BY day) ordered) seq
         WHERE training_day.day = seq.day
        """
    )
    op.alter_column("training_day", "rev", nullable=False)
    op.alter_column(
        "training_day",
        "rev",
        server_default=sa.text("nextval('training_day_rev_seq')"),
    )
    op.create_index("training_day_rev_idx", "training_day", ["rev"], unique=True)


def downgrade() -> None:
    op.drop_index("training_day_rev_idx", table_name="training_day")
    op.drop_column("training_day", "rev")
    op.execute("DROP SEQUENCE IF EXISTS training_day_rev_seq")
