"""Database configuration — async SQLAlchemy with optimized connection pooling.

Production-ready connection pool settings prevent exhaustion under load.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

settings = get_settings()

# ─── Connection Pool Configuration ─────────────────────────────────────────
# pool_size:        Base connections in pool (default 5 → set to 20)
# max_overflow:     Extra connections under burst load (10 more)
# pool_timeout:     Seconds to wait for a connection before raising
# pool_recycle:     Recycle connections after N seconds (prevent stale connections)
# pool_pre_ping:    Validate connections before use (prevents "connection closed" errors)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    # Pool tuning
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,       # Recycle every 30 minutes
    pool_pre_ping=True,
    # Query optimization
    execution_options={
        "compiled_cache": {},  # Enable query cache
    },
)

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
