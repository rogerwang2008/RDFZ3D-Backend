from typing import Optional, AsyncGenerator, Union
import re

from fastapi import Depends, Request
import fastapi_users
import fastapi_users.authentication
import fastapi_users_db_sqlmodel
from fastapi_users import models

import fastapi_users_with_username
import fastapi_users_with_username.exceptions

from . import db
from . import schemas
import universal.config

SECRET = universal.config.settings.SECRET_KEY


class UserManager(fastapi_users.UUIDIDMixin, fastapi_users_with_username.BaseUserManager[db.User, schemas.ID_TYPE]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: db.User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: db.User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: db.User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def validate_username(self, username: str, _) -> None:
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise fastapi_users_with_username.exceptions.InvalidUsernameException(
                "Username can only contain letters, numbers, and underscores.")
        if len(username) < 4:
            raise fastapi_users_with_username.exceptions.InvalidUsernameException(
                "Username must have at least 4 characters.")
        if len(username) > 100:
            raise fastapi_users_with_username.exceptions.InvalidUsernameException(
                "Username can't be longer than 100 characters.")

    async def validate_password(self, password: str, _) -> None:
        if not password.isascii():
            raise fastapi_users.exceptions.InvalidPasswordException("Password can only contain ASCII characters.")
        if len(password) < 3:
            raise fastapi_users.exceptions.InvalidPasswordException("Password should be at least 3 characters")
        if len(password) > 100:
            raise fastapi_users.exceptions.InvalidPasswordException("Password can't be longer than 100 characters.")


async def get_user_manager(user_db: fastapi_users_db_sqlmodel.SQLModelUserDatabaseAsync = Depends(db.get_user_db)) \
        -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


bearer_transport = fastapi_users.authentication.BearerTransport(tokenUrl="auth/login")


def get_database_strategy(access_token_db: fastapi_users.authentication.strategy.db.AccessTokenDatabase[db.AccessToken]
                          = Depends(db.get_access_token_db)) \
        -> fastapi_users.authentication.strategy.db.DatabaseStrategy:
    return fastapi_users.authentication.strategy.db.DatabaseStrategy(access_token_db, lifetime_seconds=60 * 60 * 24)


auth_backend = fastapi_users.authentication.AuthenticationBackend(
    name="database",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)

fastapi_users_obj = fastapi_users_with_username.FastAPIUsers[db.User, schemas.ID_TYPE](get_user_manager, [auth_backend])

current_active_user = fastapi_users_obj.current_user(active=True)
