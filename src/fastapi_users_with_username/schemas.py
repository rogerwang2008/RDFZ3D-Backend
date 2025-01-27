from typing import Optional, TypeVar, Generic
import fastapi_users.schemas
import pydantic
from pydantic import EmailStr

from . import models


class CreateUpdateDictModel(pydantic.BaseModel):
    def create_update_dict(self):
        return fastapi_users.schemas.model_dump(
            self,
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "is_email_verified",
                "is_phone_verified",
                "oauth_accounts",
            },
        )

    def create_update_dict_superuser(self):
        return fastapi_users.schemas.model_dump(self, exclude_unset=True, exclude={"id"})


class BaseUser(CreateUpdateDictModel, Generic[models.ID]):
    id: fastapi_users.models.ID
    username: str
    email: Optional[EmailStr]
    phone_no: Optional[str]
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    is_email_verified: bool = False
    is_phone_verified: bool = False

    model_config = pydantic.ConfigDict(from_attributes=True)


class BaseUserCreate(CreateUpdateDictModel):
    username: str
    email: Optional[EmailStr]
    phone_no: Optional[str]
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    is_email_verified: bool = False
    is_phone_verified: bool = False


class BaseUserUpdate(CreateUpdateDictModel):
    password: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_email_verified: bool = None
    is_phone_verified: bool = None


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)
