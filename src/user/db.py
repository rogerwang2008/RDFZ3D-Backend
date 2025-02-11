from typing import Optional, Generator

import fastapi
from sqlmodel.ext.asyncio.session import AsyncSession
import fastapi_users_db_sqlmodel.access_token

from universal import database
import fastapi_users_with_username


class User(fastapi_users_with_username.db.SQLModelBaseUserDB, table=True):
    pass


class AccessToken(fastapi_users_with_username.db.SQLModelBaseAccessToken, table=True):
    client_type: Optional[str]


async def get_user_db(session: AsyncSession = fastapi.Depends(database.get_async_session)):
    yield fastapi_users_with_username.db.SQLModelUserDatabaseAsync(session, User)


async def get_access_token_db(session: AsyncSession = fastapi.Depends(database.get_async_session)):
    yield fastapi_users_db_sqlmodel.access_token.SQLModelAccessTokenDatabaseAsync(session, AccessToken)
