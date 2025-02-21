import datetime
from typing import Optional, TYPE_CHECKING

import pydantic

from . import common


class GameServerStatusBase(pydantic.BaseModel):
    state: common.GameServerStateEnum = pydantic.Field(default=common.GameServerStateEnum.STOPPED)
    player_count: int = pydantic.Field(default=0, ge=0)
    if TYPE_CHECKING:
        game_time: Optional[datetime.datetime]
    else:
        game_time: Optional[pydantic.NaiveDatetime] = pydantic.Field(default=None)
    day_length: Optional[datetime.timedelta] = None
    night_length: Optional[datetime.timedelta] = None

    detail: Optional[str] = pydantic.Field(default=None)


class GameServerStatus(GameServerStatusBase):
    if TYPE_CHECKING:
        last_updated: Optional[datetime.datetime]
    else:
        last_updated: Optional[pydantic.AwareDatetime] = pydantic.Field(default_factory=datetime.datetime.now)
