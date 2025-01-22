from typing import Optional
from fastapi import Depends
from pydantic import BaseModel, EmailStr
from fastapi_users_db_sqlmodel import SQLModelBaseUserDB, SQLModelUserDatabaseAsync
from sqlmodel import SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from universal import database


class User(SQLModelBaseUserDB, table=True):
    email: EmailStr = Field(sa_column_kwargs={"unique": True, "index": True}, nullable=True)
    phone_no: str = Field(sa_column_kwargs={"unique": True, "index": True}, nullable=True)
    nickname: Optional[str]


async def get_user_db(session: AsyncSession = Depends(database.get_async_session)):
    yield SQLModelUserDatabaseAsync(session, User)
