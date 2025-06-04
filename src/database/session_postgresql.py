from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import get_settings

settings = get_settings()

POSTGRESQL_DATABASE_URL = (f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
                           f"{settings.POSTGRES_HOST}:{settings.POSTGRES_DB_PORT}/{settings.POSTGRES_DB}")
postgresql_engine = create_async_engine(POSTGRESQL_DATABASE_URL, echo=False)
AsyncPostgresqlSessionLocal = sessionmaker(  # type: ignore
    bind=postgresql_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

sync_database_url = POSTGRESQL_DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
sync_postgresql_engine = create_engine(sync_database_url, echo=False)


async def get_postgresql_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an asynchronous PostgreSQL database session for use within an async context.
    
    Ensures the session is properly closed after use.
    """
    async with AsyncPostgresqlSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_postgresql_db_contextmanager() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous context manager that yields a PostgreSQL database session.
    
    Yields:
        An AsyncSession instance for use within an async `with` statement. The session is automatically closed when the context exits.
    """
    async with AsyncPostgresqlSessionLocal() as session:
        yield session
