import datetime
from typing import Any, Optional

import user.schemas
from . import models, common


class UserInfoCreate(models.UserInfoVisibility, models.UserInfoBase):
    pass


class UserFullCreate(models.UserInfoVisibility, models.UserInfoBase, user.schemas.UserCreate):
    pass


class UserFullReadAdmin(models.UserInfo, user.schemas.UserRead, table=False):
    pass


class UserFullRead(models.UserInfoBase, user.schemas.UserReadSafe):
    pass


class UserFullUpdate(models.UserInfoVisibility, models.UserInfoBase, user.schemas.UserUpdate):
    nickname: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[common.GenderEnum] = None
    birthday: Optional[datetime.date] = None
    identity: Optional[str] = None
