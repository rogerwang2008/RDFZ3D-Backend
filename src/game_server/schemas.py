from typing import Optional
import pydantic
from pydantic.networks import IPvAnyAddress

from . import models
from .status import common as status_common
from .status import crud as status_crud
from .status import models as status_models


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
    status: status_models.GameServerStatusBase = None

    @pydantic.model_validator(mode="after")
    def set_status(self) -> "GameServerRead":
        if self.status is None:
            self.status = status_crud.get_server_status(self.id)
        return self


class GameServerReadAdmin(models.GameServerPublic, models.GameServerId, table=False):
    """管理员读取游戏服务器信息的 schema"""
    reporter_host: IPvAnyAddress
    status: status_models.GameServerStatusBase = None

    @pydantic.model_validator(mode="after")
    def set_status(self) -> "GameServerReadAdmin":
        if self.status is None:
            self.status = status_crud.get_server_status(self.id)
        return self
