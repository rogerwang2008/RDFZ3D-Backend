from typing import Optional

import datetime
import json
import fastapi
import sqlalchemy
from sqlalchemy.dialects.mysql import LONGTEXT
import sqlmodel
import pydantic

import universal.database
from . import common


class GameServerId(sqlmodel.SQLModel):
    """用于使自动生成的文档、数据库行顺序正确"""
    id: int


class GameServerBase(sqlmodel.SQLModel):
    address: str = sqlmodel.Field(index=True, unique=True)
    name: str = sqlmodel.Field(index=True, unique=True)
    description: Optional[str] = sqlmodel.Field(nullable=False, default="")
    detail: Optional[str] = sqlmodel.Field(default=None, sa_type=LONGTEXT)


class GameServerPublic(GameServerBase):
    # noinspection PyTypeChecker
    admin: Optional[str] = sqlmodel.Field(foreign_key="user.id", nullable=True, sa_type=sqlalchemy.CHAR(26),
                                          default=None)


class GameServer(GameServerPublic, GameServerId, table=True):
    __tablename__ = "game_server"
    id: Optional[int] = sqlmodel.Field(primary_key=True, default=None)
    reporter_host: str


class GameServerStatusBase(pydantic.BaseModel):
    player_count: int = pydantic.Field(default=0, ge=0)
    state: common.GameServerState = pydantic.Field(default=common.GameServerState.STOPPED)


class GameServerStatus(GameServerStatusBase):
    last_updated: Optional[pydantic.AwareDatetime] = pydantic.Field(default_factory=datetime.datetime.now)
