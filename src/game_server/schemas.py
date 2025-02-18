from typing import Optional
import pydantic
from pydantic.networks import IPvAnyAddress

from . import models
from .status.common import GameServerStateEnum
from .status.models import GameServerStatusBase, GameServerStatus


class GameServerCreate(models.GameServerBase):
    """创建游戏服务器的 schema"""
    reporter_host: IPvAnyAddress


class GameServerUpdate(models.GameServerBase):
    """更新游戏服务器信息的 schema"""
    address: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    detail: Optional[str] = None
    reporter_host: Optional[IPvAnyAddress] = None


class GameServerRead(models.GameServerPublic, models.GameServerId):
    """读取游戏服务器信息的 schema"""
    status: GameServerStatusBase = pydantic.Field(
        default=GameServerStatusBase(player_count=0, state=GameServerStateEnum.STOPPED))


class GameServerReadAdmin(models.GameServerPublic, models.GameServerId, table=False):
    """管理员读取游戏服务器信息的 schema"""
    reporter_host: IPvAnyAddress
    status: GameServerStatus = pydantic.Field(
        default=GameServerStatus(player_count=0, state=GameServerStateEnum.STOPPED, last_updated=None))
