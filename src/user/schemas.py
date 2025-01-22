from typing import Optional
import uuid
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    phone_no: str
    nickname: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    phone_no: str
    nickname: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    phone_no: Optional[str] = None
    nickname: Optional[str] = None

