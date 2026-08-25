# API

FastAPI + SQLAlchemy 2.0 async + Alembic. Postgres: локально обычный,
в облаке — Neon.

## Запуск

```
uv sync --all-groups
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 4318
```

Схема OpenAPI: http://localhost:4318/docs

## Настройки

Копируй `.env.example` в `.env`.

| | |
|---|---|
| `DATABASE_URL` | локально обычная строка, на Vercel — **пулированная** строка Neon |
| `API_TOKEN` | пустой = проверка выключена. В облаке обязателен |
| `CORS_ORIGINS` | через запятую; `app://tracker` — бандл внутри macOS-приложения |
| `SERVERLESS` | `true` на Vercel: соединения не пулируются в процессе |

## Эндпоинты

| | | |
|---|---|---|
| GET | `/api/health` | без токена |
| GET | `/api/entries?from=&to=` | диапазон дат |
| GET | `/api/changes?since=&limit=` | дельта по курсору `rev` |
| PUT | `/api/entries/{day}` | одна запись |
| POST | `/api/entries/batch` | выгрузка офлайн-очереди |
| GET | `/api/today?day=` | отметки дня и прогресс недели |
| POST | `/api/today/toggle?day=` | переключить `yoga` или `gym` |
| GET | `/api/stats?year=&day=` | счётчики за год и серия йоги |
| GET | `/api/export` · POST `/api/import` | JSON целиком |
| GET | `/api/plan` | план недели из `packages/plan/plan.json` |

**Параметр `day` обязателен для клиентов.** Сервер живёт в UTC, и своей дате
доверять нельзя: отметка в час ночи по Москве ушла бы во вчерашний день.
Клиент всегда присылает свою локальную дату.

## Ловушки Vercel

**Пул соединений.** Функция короткоживущая, свой пул выжрет лимит Neon за день.
`SERVERLESS=true` включает `NullPool`, пулирует Neon на своей стороне.

**Миграции не идут в рантайме.** `alembic upgrade head` катится отдельным шагом:
локально против Neon или из CI.

**Фоновых задач нет.** Сейчас не нужны; если понадобятся — это будет отдельный
механизм, а не поток внутри сервера.

## Миграции

| | |
|---|---|
| `0001` | исходная таблица дней |
| `0002` | колонка `rev`, последовательность и индекс под дельта-синхронизацию |

Если база уже существует со схемой `0001`: `alembic stamp 0001`, затем `upgrade head`.
