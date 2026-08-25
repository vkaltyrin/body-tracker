from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from .config import settings

_cfg = settings()

# NullPool на Vercel — обязателен: функция короткоживущая, свой пул там
# только выжрет лимит соединений Neon. Пулирует Neon на своей стороне.
engine = create_async_engine(
    _cfg.database_url,
    poolclass=NullPool if _cfg.serverless else None,
    pool_pre_ping=not _cfg.serverless,
    echo=False,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as s:
        yield s
