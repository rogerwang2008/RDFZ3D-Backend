import datetime
from typing import Any, Optional

import pydantic

import user.schemas
from . import models, common


class UserInfoCreate(models.UserInfoVisibility, models.UserInfoBase):
    pass


class UserFullCreate(models.UserInfoVisibility, models.UserInfoBase, user.schemas.UserCreate):
    nickname: Optional[str] = None

    @pydantic.model_validator(mode="after")
    def set_default_nickname(self) -> "UserFullCreate":
        if self.nickname is None:
            self.nickname = self.username
        return self


class UserFullReadAdmin(models.UserInfo, user.schemas.UserRead, table=False):
    pass


class UserFullRead(models.UserInfoBase, user.schemas.UserReadSafe):
    pass


class UserFullUpdate(models.UserInfoVisibility, models.UserInfoBase, user.schemas.UserUpdate):
    nickname: Optional[str] = None
