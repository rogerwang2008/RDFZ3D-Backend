from typing import Optional
import fastapi
import pydantic
import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.functions import func

from universal import database
import fastapi_users_with_username


class User(fastapi_users_with_username.db.SQLModelBaseUserDB, table=True):
    pass


async def get_user_db(session: AsyncSession = fastapi.Depends(database.get_async_session)):
    yield fastapi_users_with_username.db.SQLModelUserDatabaseAsync(session, User)
