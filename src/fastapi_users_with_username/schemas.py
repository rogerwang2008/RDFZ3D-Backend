from typing import Optional, TypeVar
import fastapi_users.models
from pydantic import EmailStr


class BaseUser(fastapi_users.schemas.BaseUser[fastapi_users.models.ID]):
    id: fastapi_users.models.ID
    username: str
    email: Optional[EmailStr]
    phone_no: Optional[str]
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class BaseUserCreate(fastapi_users.schemas.BaseUserCreate):
    username: str
    email: Optional[EmailStr]
    phone_no: Optional[str]
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class BaseUserUpdate(fastapi_users.schemas.BaseUserUpdate):
    password: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)
