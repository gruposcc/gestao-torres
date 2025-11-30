# from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.settings import DB_URL

engine = create_async_engine(DB_URL, echo=False)
SessionLocal = async_sessionmaker[AsyncSession](
    engine, expire_on_commit=False, class_=AsyncSession
)


# asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
