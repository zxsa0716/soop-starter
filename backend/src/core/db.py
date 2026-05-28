"""PostgreSQL + PostGIS connection (asyncpg + SQLAlchemy 2.0)."""
from __future__ import annotations
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from .config import settings


_engine = None
_session_maker = None


def get_engine():
    global _engine
    if _engine is None:
        dsn = settings.postgres_dsn.replace("psycopg2", "asyncpg")
        _engine = create_async_engine(dsn, pool_pre_ping=True, pool_size=10)
    return _engine


def get_session_maker():
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _session_maker


@asynccontextmanager
async def session_scope():
    async with get_session_maker()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
