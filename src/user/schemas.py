from typing import Optional, TYPE_CHECKING

import pydantic
import ulid
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

import fastapi_users_with_username

ID_TYPE = ulid.ULID  # 写死了 千万别想着改回 UUID 了


class UserRead(fastapi_users_with_username.schemas.BaseUser[ID_TYPE]):
    pass


class UserReadSafe(pydantic.BaseModel):
    id: ID_TYPE
    username: str
    if TYPE_CHECKING:
        email: Optional[str] = None
    else:
        email: Optional[EmailStr] = None
    phone_no: Optional[PhoneNumber] = None
    is_superuser: bool = False
    is_verified: bool = False



class UserCreate(fastapi_users_with_username.schemas.BaseUserCreate):
    pass


class UserUpdate(fastapi_users_with_username.schemas.BaseUserUpdate):
    pass


class UserLogin(fastapi_users_with_username.schemas.BaseUserLogin):
    client_type: Optional[str] = None
    unique: bool = False
