import asyncio
import sys

from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings

DB_POOL_SIZE = 83
WEB_CONCURRENCY = 9
POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)

if "win" in sys.platform:
    # Set event loop policy for Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

connect_args = {"check_same_thread": False}

db_url = settings.PSQL_DATABASE_URL
if hasattr(db_url, 'unicode_string'):
    engine = create_async_engine(
        db_url.unicode_string(),
        echo=False,
        future=True,
        pool_size=POOL_SIZE,
        max_overflow=64,
        poolclass=AsyncAdaptedQueuePool,
    )
else:
    engine = create_async_engine(
        db_url.encode('utf-8').decode('unicode_escape'),
        echo=False,
        future=True,
        pool_size=POOL_SIZE,
        max_overflow=64,
        poolclass=AsyncAdaptedQueuePool,
    )


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
