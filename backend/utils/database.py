from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine, event
from models.generation import Base
from config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

# ── Engine configuration ────────────────────────────────────────
_db_url = settings.EFFECTIVE_DATABASE_URL
_db_url_sync = settings.EFFECTIVE_DATABASE_URL_SYNC
_is_sqlite = settings.USE_SQLITE

# Async engine for FastAPI
_engine_kwargs: dict = dict(
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Check if connection is alive before using it
)

if not _is_sqlite:
    _engine_kwargs.update(
        pool_size=20,            # Max persistent connections
        max_overflow=10,         # Max extra temporary connections under load
        pool_recycle=1800,       # Recycle connections after 30 minutes
        pool_timeout=30,         # Wait up to 30 seconds for a connection
    )

async_engine = create_async_engine(_db_url, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine for Celery workers
_sync_kwargs: dict = dict(
    pool_pre_ping=True,
)

if _is_sqlite:
    # SQLite needs check_same_thread=False for multi-threaded Celery
    _sync_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _sync_kwargs.update(
        pool_size=10,
        max_overflow=5,
        pool_recycle=1800,
    )

sync_engine = create_engine(_db_url_sync, **_sync_kwargs)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    max_retries = 6
    retry_delay = 2
    for attempt in range(1, max_retries + 1):
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info(f"Database tables created/verified successfully. (backend: {'sqlite' if _is_sqlite else 'postgres'})")
            return
        except Exception as e:
            if attempt == max_retries:
                logger.critical(f"Database connection failed after {max_retries} attempts. Aborting.")
                raise e
            logger.warning(
                f"Database connection attempt {attempt}/{max_retries} failed: {e}. "
                f"Retrying in {retry_delay}s..."
            )
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
