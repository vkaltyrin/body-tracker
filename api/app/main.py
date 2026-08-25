import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import repo
from .config import settings
from .db import session
from .schemas import (
    BatchRequest,
    BatchResult,
    Changes,
    Entry,
    EntryPatch,
    ExportFile,
    ImportRequest,
    ImportResult,
    Stats,
    Target,
    Today,
    ToggleRequest,
    WeekProgress,
)

cfg = settings()
Session = Annotated[AsyncSession, Depends(session)]

app = FastAPI(
    title="Body tracker",
    version="0.1.0",
    description="Трекер тренировок: отметки по дням, дельта-синхронизация, план.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def guard(authorization: Annotated[str | None, Header()] = None) -> None:
    """Один статический токен. Пустой в настройках — проверка выключена.

    Приложение однопользовательское, поэтому ни аккаунтов, ни сессий здесь нет:
    токен нужен только чтобы публичный адрес не мог править кто угодно.
    """
    if not cfg.api_token:
        return
    if authorization != f"Bearer {cfg.api_token}":
        raise HTTPException(status_code=401, detail="Нужен корректный токен.")


Guarded = Depends(guard)


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def client_day(day: date | None) -> date:
    """Сегодняшний день с точки зрения клиента.

    Сервер живёт в UTC, поэтому спрашивать дату у него нельзя: отметка в час ночи
    по Москве ушла бы во вчерашний день. Клиент всегда присылает свою дату сам.
    """
    return day or datetime.now(timezone.utc).date()


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/entries", response_model=list[Entry], dependencies=[Guarded])
async def entries(
    s: Session,
    date_from: Annotated[date, Query(alias="from")],
    date_to: Annotated[date, Query(alias="to")],
) -> list[Entry]:
    if date_to < date_from:
        raise HTTPException(400, "Конец периода раньше начала.")
    return await repo.get_range(s, date_from, date_to)


@app.get("/api/changes", response_model=Changes, dependencies=[Guarded])
async def changes(
    s: Session,
    since: int = 0,
    limit: Annotated[int, Query(ge=1, le=5000)] = 1000,
) -> Changes:
    """Всё, что изменилось после курсора клиента."""
    items, cursor, has_more = await repo.get_changes(s, since, limit)
    return Changes(entries=items, cursor=cursor, has_more=has_more)


@app.put("/api/entries/{day}", response_model=Entry, dependencies=[Guarded])
async def put_entry(s: Session, day: date, patch: EntryPatch) -> Entry:
    entry, _ = await repo.upsert(s, day, patch)
    await s.commit()
    return entry


@app.post("/api/entries/batch", response_model=BatchResult, dependencies=[Guarded])
async def batch(s: Session, req: BatchRequest) -> BatchResult:
    """Выгрузка офлайн-очереди целиком.

    Пропущенные изменения — не ошибка: значит, в базе лежит более свежая версия.
    """
    applied, skipped = await repo.apply_batch(s, req.entries)
    cursor = await repo.current_rev(s)
    await s.commit()
    return BatchResult(applied=applied, skipped=skipped, cursor=cursor)


@app.get("/api/today", response_model=Today, dependencies=[Guarded])
async def today(s: Session, day: date | None = None) -> Today:
    d = client_day(day)
    monday = monday_of(d)
    sunday = monday + timedelta(days=6)
    entry = await repo.get_one(s, d)
    yoga, gym = await repo.week_counts(s, monday, sunday)
    return Today(
        today=d,
        yoga_done=bool(entry and entry.yoga),
        gym_done=bool(entry and entry.gym),
        week=WeekProgress(**{"from": monday, "to": sunday, "yoga": yoga, "gym": gym}),
        target=Target(yoga=cfg.target_yoga, gym=cfg.target_gym),
    )


@app.post("/api/today/toggle", response_model=Entry, dependencies=[Guarded])
async def toggle_today(s: Session, req: ToggleRequest, day: date | None = None) -> Entry:
    if req.field not in ("yoga", "gym"):
        raise HTTPException(400, 'Поле должно быть "yoga" или "gym".')
    entry = await repo.toggle(s, client_day(day), req.field)
    await s.commit()
    return entry


@app.get("/api/stats", response_model=Stats, dependencies=[Guarded])
async def stats(s: Session, year: int | None = None, day: date | None = None) -> Stats:
    d = client_day(day)
    y = year or d.year
    yoga, gym, both = await repo.year_counts(s, y)
    return Stats(year=y, yoga=yoga, gym=gym, both=both, yoga_streak=await repo.yoga_streak(s, d))


@app.get("/api/export", response_model=ExportFile, dependencies=[Guarded])
async def export(s: Session) -> ExportFile:
    return ExportFile(exported_at=datetime.now(timezone.utc), entries=await repo.all_entries(s))


@app.post("/api/import", response_model=ImportResult, dependencies=[Guarded])
async def import_entries(s: Session, req: ImportRequest) -> ImportResult:
    if req.mode not in ("merge", "replace"):
        raise HTTPException(400, 'Режим должен быть "merge" или "replace".')
    if req.mode == "replace":
        await repo.truncate(s)
    applied, skipped = await repo.apply_batch(s, req.entries)
    await s.commit()
    return ImportResult(imported=applied, skipped=skipped, mode=req.mode)


PLAN_PATHS = [
    Path(__file__).resolve().parents[2] / "packages" / "plan" / "plan.json",
    Path(__file__).resolve().parent / "data" / "plan.json",
]


@app.get("/api/plan", dependencies=[Guarded])
async def plan() -> dict:
    """План недели как данные. Источник правды — plan.json под гитом."""
    for path in PLAN_PATHS:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise HTTPException(500, "Файл плана не найден.")
