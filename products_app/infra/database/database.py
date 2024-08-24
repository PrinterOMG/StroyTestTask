from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


def new_engine(database_uri: str) -> AsyncEngine:
    return create_async_engine(
        database_uri,
        pool_size=15,
        max_overflow=15,
    )


def new_session_maker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
