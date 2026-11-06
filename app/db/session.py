from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,       # where to connect
    pool_pre_ping=True,
    echo=False,
    connect_args={"timeout": 5},  # fail fast if the host is unreachable
)

SessionLocal = async_sessionmaker(
    bind=engine,                 # which engine do sessions borrow connections from?
    expire_on_commit=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
