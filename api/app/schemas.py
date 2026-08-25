from datetime import date, datetime

from pydantic import BaseModel, Field


class Entry(BaseModel):
    """Один тренировочный день."""

    day: date
    yoga: bool = False
    gym: bool = False
    note: str = ""
    updated_at: datetime
    rev: int


class EntryPatch(BaseModel):
    """Изменение дня, пришедшее от клиента.

    `updated_at` ставит клиент в момент нажатия — в том числе офлайн.
    При конфликте побеждает большее значение, поэтому отправленная позже
    из очереди старая отметка не затрёт более свежую.
    """

    yoga: bool = False
    gym: bool = False
    note: str = Field(default="", max_length=2000)
    updated_at: datetime | None = None


class BatchItem(EntryPatch):
    day: date


class BatchRequest(BaseModel):
    entries: list[BatchItem]


class BatchResult(BaseModel):
    applied: int
    skipped: int
    cursor: int


class Changes(BaseModel):
    """Дельта для клиента: всё, что изменилось после его курсора."""

    entries: list[Entry]
    cursor: int
    has_more: bool = False


class ToggleRequest(BaseModel):
    field: str


class WeekProgress(BaseModel):
    from_: date = Field(alias="from")
    to: date
    yoga: int
    gym: int

    model_config = {"populate_by_name": True}


class Target(BaseModel):
    yoga: int
    gym: int


class Today(BaseModel):
    today: date
    yoga_done: bool
    gym_done: bool
    week: WeekProgress
    target: Target


class Stats(BaseModel):
    year: int
    yoga: int
    gym: int
    both: int
    yoga_streak: int


class ExportFile(BaseModel):
    version: int = 1
    exported_at: datetime
    entries: list[Entry]


class ImportRequest(BaseModel):
    entries: list[BatchItem]
    mode: str = "merge"


class ImportResult(BaseModel):
    imported: int
    skipped: int
    mode: str
