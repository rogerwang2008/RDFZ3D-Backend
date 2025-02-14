import datetime
from typing import Optional, TYPE_CHECKING

import pydantic

from . import common


class GameServerStatusBase(pydantic.BaseModel):
    player_count: int = pydantic.Field(default=0, ge=0)
    state: common.GameServerStateEnum = pydantic.Field(default=common.GameServerStateEnum.STOPPED)


class GameServerStatus(GameServerStatusBase):
    if TYPE_CHECKING:
        last_updated: Optional[datetime.datetime]
    else:
        last_updated: Optional[pydantic.AwareDatetime] = pydantic.Field(default_factory=datetime.datetime.now)
