from typing import Optional, TypeVar, Generic, TYPE_CHECKING
import fastapi_users.schemas
import pydantic
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from . import models

PhoneNumber.default_region_code = "CN"
PhoneNumber.phone_format = "E164"


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
    if TYPE_CHECKING:
        email: Optional[str]
    else:
        email: Optional[EmailStr]
    phone_no: Optional[PhoneNumber]
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    is_email_verified: bool = False
    is_phone_verified: bool = False

    model_config = pydantic.ConfigDict(from_attributes=True)


class BaseUserCreate(CreateUpdateDictModel):
    username: str
    if TYPE_CHECKING:
        email: Optional[str]
    else:
        email: Optional[EmailStr]
    phone_no: Optional[PhoneNumber]
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    is_email_verified: bool = False
    is_phone_verified: bool = False


class BaseUserUpdate(CreateUpdateDictModel):
    password: Optional[str] = None
    username: Optional[str] = None
    if TYPE_CHECKING:
        email: Optional[str] = None
    else:
        email: Optional[EmailStr] = None
    phone_no: Optional[PhoneNumber] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_email_verified: bool = None
    is_phone_verified: bool = None


class BaseUserLogin(pydantic.BaseModel):
    username: str
    password: str


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)
UL = TypeVar("UL", bound=BaseUserLogin)
