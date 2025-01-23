import uuid
from typing import Optional, AsyncGenerator

from fastapi import Depends, Request
import fastapi_users
import fastapi_users.authentication
import fastapi_users_db_sqlmodel
import fastapi_users_with_username

from .db import User, get_user_db
import universal.config

SECRET = universal.config.settings.SECRET_KEY


class UserManager(fastapi_users.UUIDIDMixin, fastapi_users_with_username.BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: fastapi_users_db_sqlmodel.SQLModelUserDatabaseAsync = Depends(get_user_db)) \
        -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


bearer_transport = fastapi_users.authentication.BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> fastapi_users.authentication.JWTStrategy[fastapi_users.models.UP, fastapi_users.models.ID]:
    return fastapi_users.authentication.JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = fastapi_users.authentication.AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users_obj = fastapi_users.FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users_obj.current_user(active=True)
