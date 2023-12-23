import logging
from typing import AsyncIterator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from settings import settings

logger = logging.getLogger(__name__)

async_engine = create_async_engine(
    settings.DB_DSN,
    pool_pre_ping=True,
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    future=True,
)


async def get_session() -> AsyncIterator[async_sessionmaker]:
    try:
        yield AsyncSessionLocal
    except SQLAlchemyError as e:
        logger.exception(e)


async def ping_database():
    try:
        async with async_engine.begin():
            # Ping the database by executing a simple query
            pass
        logger.info("Database connection is active and responsive!")
    except Exception as e:
        logger.exception("Error pinging database:", e)
        raise SystemExit(1)
