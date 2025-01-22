from typing import AsyncGenerator

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import settings

connect_args = {}
engine = create_async_engine(settings.DATABASE_URI, echo=True, connect_args=connect_args)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    # SQLModel.metadata.create_all(engine)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    # with AsyncSession(engine) as session:
    #     yield session
    async with async_session_maker() as session:
        yield session
