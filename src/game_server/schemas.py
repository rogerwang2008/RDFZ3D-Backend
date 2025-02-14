from typing import Optional
import pydantic
from pydantic.networks import IPvAnyAddress

from . import models, common


class GameServerCreate(models.GameServerBase):
    """创建游戏服务器的 schema"""
    reporter_host: IPvAnyAddress


class GameServerUpdate(models.GameServerBase):
    """更新游戏服务器信息的 schema"""
    address: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    detail: Optional[str] = None


class GameServerRead(models.GameServerPublic, models.GameServerId):
    """读取游戏服务器信息的 schema"""
    status: models.GameServerStatusBase = pydantic.Field(
        default=models.GameServerStatusBase(player_count=0, state=common.GameServerState.STOPPED))


class GameServerReadAdmin(models.GameServerPublic, models.GameServerId, table=False):
    """管理员读取游戏服务器信息的 schema"""
    reporter_host: IPvAnyAddress
    status: models.GameServerStatus = pydantic.Field(
        default=models.GameServerStatus(player_count=0, state=common.GameServerState.STOPPED, last_updated=None))


class GameServerReport(models.GameServerStatusBase, models.GameServerId):
    """游戏服务器上报状态的 schema"""
    pass
