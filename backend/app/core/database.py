"""Database configuration — async SQLAlchemy with optimized connection pooling.

Production-ready connection pool settings prevent exhaustion under load.
"""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

settings = get_settings()

# Allow overriding DATABASE_URL for tests (set before this module imports)
DATABASE_URL = os.environ.get("DATABASE_URL") or settings.DATABASE_URL

# Pool settings only apply to non-SQLite backends
_is_sqlite = DATABASE_URL.startswith("sqlite")
_engine_kwargs = {
    "echo": False,
    **({} if _is_sqlite else {
        "pool_size": 20,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }),
}

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency that yields a database session with automatic commit/rollback."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine():
    """Dispose of the engine connection pool (for graceful shutdown)."""
    await engine.dispose()
