from typing import Optional
import datetime

import sqlalchemy
import sqlmodel

from . import common


class UserInfoId(sqlmodel.SQLModel):
    id: str = sqlmodel.Field(primary_key=True, foreign_key="user.id", sa_type=sqlalchemy.CHAR(26))
    # user_auth: user.db.User = sqlmodel.Relationship(back_populates="user_info")


class UserInfoBase(sqlmodel.SQLModel):
    nickname: Optional[str]
    real_name: Optional[str]
    gender: Optional[common.GenderEnum]
    birthday: Optional[datetime.date]
    identity: Optional[str]


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

