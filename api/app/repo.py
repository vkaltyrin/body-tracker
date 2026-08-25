"""Работа с таблицей дней.

Два правила, на которых держится синхронизация:

* `rev` — монотонная ревизия сервера. Клиент хранит последнюю виденную и просит
  всё, что больше. Так дельта не зависит от часов и часовых поясов.
* `updated_at` — время клиента в момент нажатия. При конфликте побеждает большее.
  Поэтому отметка, пролежавшая в офлайн-очереди, не затрёт более свежую с другого
  устройства.
"""

from datetime import date, datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import BatchItem, Entry, EntryPatch

FIELDS = ("day", "yoga", "gym", "note", "updated_at", "rev")
_SELECT = "SELECT day, yoga, gym, note, updated_at, rev FROM training_day"

UPSERT = text(
    """
    INSERT INTO training_day (day, yoga, gym, note, updated_at, rev)
    VALUES (:day, :yoga, :gym, :note, :updated_at, nextval('training_day_rev_seq'))
    ON CONFLICT (day) DO UPDATE
       SET yoga = EXCLUDED.yoga,
           gym = EXCLUDED.gym,
           note = EXCLUDED.note,
           updated_at = EXCLUDED.updated_at,
           rev = nextval('training_day_rev_seq')
     WHERE EXCLUDED.updated_at >= training_day.updated_at
    RETURNING day, yoga, gym, note, updated_at, rev
    """
)


def _entry(row) -> Entry:
    return Entry(**dict(zip(FIELDS, row, strict=True)))


async def get_range(s: AsyncSession, since: date, until: date) -> list[Entry]:
    rows = await s.execute(
        text(f"{_SELECT} WHERE day BETWEEN :a AND :b ORDER BY day"), {"a": since, "b": until}
    )
    return [_entry(r) for r in rows]


async def get_changes(s: AsyncSession, since: int, limit: int) -> tuple[list[Entry], int, bool]:
    rows = await s.execute(
        text(f"{_SELECT} WHERE rev > :since ORDER BY rev LIMIT :limit"),
        {"since": since, "limit": limit + 1},
    )
    entries = [_entry(r) for r in rows]
    has_more = len(entries) > limit
    entries = entries[:limit]
    cursor = entries[-1].rev if entries else since
    return entries, cursor, has_more


async def get_one(s: AsyncSession, day: date) -> Entry | None:
    row = (await s.execute(text(f"{_SELECT} WHERE day = :d"), {"d": day})).first()
    return _entry(row) if row else None


async def upsert(s: AsyncSession, day: date, patch: EntryPatch) -> tuple[Entry, bool]:
    """Возвращает актуальную запись и признак, что изменение применилось.

    Не применилось — значит в базе лежит более свежая версия, и это нормальный
    исход при доставке из офлайн-очереди, а не ошибка.
    """
    stamp = patch.updated_at or datetime.now(timezone.utc)
    row = (
        await s.execute(
            UPSERT,
            {
                "day": day,
                "yoga": patch.yoga,
                "gym": patch.gym,
                "note": patch.note,
                "updated_at": stamp,
            },
        )
    ).first()
    if row:
        return _entry(row), True
    current = await get_one(s, day)
    assert current is not None  # строка есть: иначе INSERT бы прошёл
    return current, False


async def apply_batch(s: AsyncSession, items: list[BatchItem]) -> tuple[int, int]:
    applied = skipped = 0
    for item in items:
        _, ok = await upsert(s, item.day, EntryPatch(**item.model_dump(exclude={"day"})))
        applied += ok
        skipped += not ok
    return applied, skipped


async def current_rev(s: AsyncSession) -> int:
    row = (await s.execute(text("SELECT coalesce(max(rev), 0) FROM training_day"))).first()
    return int(row[0]) if row else 0


async def toggle(s: AsyncSession, day: date, field: str) -> Entry:
    if field not in ("yoga", "gym"):
        raise ValueError(field)
    row = (
        await s.execute(
            text(
                f"""
                INSERT INTO training_day (day, {field}, updated_at, rev)
                VALUES (:day, true, now(), nextval('training_day_rev_seq'))
                ON CONFLICT (day) DO UPDATE
                   SET {field} = NOT training_day.{field},
                       updated_at = now(),
                       rev = nextval('training_day_rev_seq')
                RETURNING day, yoga, gym, note, updated_at, rev
                """
            ),
            {"day": day},
        )
    ).first()
    return _entry(row)


async def week_counts(s: AsyncSession, monday: date, sunday: date) -> tuple[int, int]:
    row = (
        await s.execute(
            text(
                """
                SELECT count(*) FILTER (WHERE yoga), count(*) FILTER (WHERE gym)
                  FROM training_day WHERE day BETWEEN :a AND :b
                """
            ),
            {"a": monday, "b": sunday},
        )
    ).first()
    return int(row[0]), int(row[1])


async def year_counts(s: AsyncSession, year: int) -> tuple[int, int, int]:
    row = (
        await s.execute(
            text(
                """
                SELECT count(*) FILTER (WHERE yoga),
                       count(*) FILTER (WHERE gym),
                       count(*) FILTER (WHERE yoga AND gym)
                  FROM training_day WHERE day BETWEEN :a AND :b
                """
            ),
            {"a": date(year, 1, 1), "b": date(year, 12, 31)},
        )
    ).first()
    return int(row[0]), int(row[1]), int(row[2])


async def yoga_streak(s: AsyncSession, today: date) -> int:
    """Серия подряд идущих дней с йогой, считая назад от сегодня.

    Сегодняшний день ещё может быть не отмечен — тогда серия считается от вчера,
    иначе каждое утро обнуляло бы её.
    """
    rows = await s.execute(
        text("SELECT day FROM training_day WHERE yoga AND day <= :d ORDER BY day DESC LIMIT 400"),
        {"d": today},
    )
    done = {r[0] for r in rows}
    cursor = today if today in done else date.fromordinal(today.toordinal() - 1)
    streak = 0
    while cursor in done:
        streak += 1
        cursor = date.fromordinal(cursor.toordinal() - 1)
    return streak


async def all_entries(s: AsyncSession) -> list[Entry]:
    rows = await s.execute(text(f"{_SELECT} ORDER BY day"))
    return [_entry(r) for r in rows]


async def truncate(s: AsyncSession) -> None:
    await s.execute(text("TRUNCATE training_day"))
