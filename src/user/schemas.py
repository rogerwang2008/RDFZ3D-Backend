from typing import Optional

import ulid

import fastapi_users_with_username

ID_TYPE = ulid.ULID  # 写死了 千万别想着改回 UUID 了


class UserRead(fastapi_users_with_username.schemas.BaseUser[ID_TYPE]):
    pass


class UserCreate(fastapi_users_with_username.schemas.BaseUserCreate):
    pass


class UserUpdate(fastapi_users_with_username.schemas.BaseUserUpdate):
    pass


class UserLogin(fastapi_users_with_username.schemas.BaseUserLogin):
    client_type: Optional[str] = None

