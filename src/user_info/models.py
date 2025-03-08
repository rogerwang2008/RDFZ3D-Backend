from typing import Optional
import datetime

import sqlalchemy
import sqlmodel

from . import common


class UserInfoId(sqlmodel.SQLModel):
    # noinspection PyTypeChecker
    id: str = sqlmodel.Field(primary_key=True, foreign_key="user.id", sa_type=sqlalchemy.CHAR(26))


class UserInfoBase(sqlmodel.SQLModel):
    nickname: str
    avatar_path: str = "/assets/avatar/default_avatar.png"
    real_name: Optional[str] = None
    gender: Optional[common.GenderEnum] = None
    birthday: Optional[datetime.date] = None
    identity: Optional[str] = None


class UserInfoVisibility(sqlmodel.SQLModel):
    email_public: bool = False
    phone_no_public: bool = False
    is_superuser_public: bool = True
    real_name_public: bool = True
    gender_public: bool = True
    birthday_public: bool = True
    identity_public: bool = True


class UserInfo(UserInfoVisibility, UserInfoBase, UserInfoId, table=True):
    __tablename__ = "user_info"

