from typing import Any

import user.schemas
from . import models


class UserInfoCreate(models.UserInfoVisibility, models.UserInfoBase):
    pass


class UserFullCreate(models.UserInfoVisibility, models.UserInfoBase, user.schemas.UserCreate):
    pass


class UserFullReadAdmin(models.UserInfo, user.schemas.UserRead, table=False):
    pass
