from typing import Optional
import fastapi
import pydantic
import fastapi_users_db_sqlmodel
import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.functions import func

from universal import database
import fastapi_users_with_username


class User(fastapi_users_db_sqlmodel.SQLModelBaseUserDB, table=True):
    username: str = sqlmodel.Field(sa_column_kwargs={"unique": True, "index": True})
    email: Optional[pydantic.EmailStr] = sqlmodel.Field(sa_column_kwargs={"unique": True, "index": True}, nullable=True)
    phone_no: Optional[str] = sqlmodel.Field(sa_column_kwargs={"unique": True, "index": True}, nullable=True)
    nickname: Optional[str]


async def get_user_db(session: AsyncSession = fastapi.Depends(database.get_async_session)):
    yield fastapi_users_with_username.db.SQLModelUserDatabaseAsync(session, User)
