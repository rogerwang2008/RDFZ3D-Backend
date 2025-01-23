import uuid

import fastapi_users_with_username


class UserRead(fastapi_users_with_username.schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(fastapi_users_with_username.schemas.BaseUserCreate):
    pass


class UserUpdate(fastapi_users_with_username.schemas.BaseUserUpdate):
    pass

