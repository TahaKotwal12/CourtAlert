import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from app.core.config import settings

_is_serverless = os.environ.get("VERCEL") == "1"

# NeonDB requires SSL. Pass "require" via connect_args — asyncpg ignores URL query params.
# Serverless environments can't maintain a connection pool, so use NullPool on Vercel.
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.APP_ENV == "development",
    pool_pre_ping=not _is_serverless,
    **({"poolclass": NullPool} if _is_serverless else {"pool_size": 5, "max_overflow": 10}),
    connect_args={"ssl": "require"},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
