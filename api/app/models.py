from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Sequence, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# Монотонный счётчик ревизий: по нему клиенты забирают дельту изменений.
rev_seq = Sequence("training_day_rev_seq")


class TrainingDay(Base):
    __tablename__ = "training_day"

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    yoga: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    gym: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    note: Mapped[str] = mapped_column(String, nullable=False, server_default=text("''"))

    # Время клиента. По нему разрешается конфликт: побеждает большее.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Ревизия сервера. По ней идёт дельта-синхронизация, к конфликтам отношения не имеет.
    rev: Mapped[int] = mapped_column(
        BigInteger, rev_seq, nullable=False, server_default=rev_seq.next_value()
    )
