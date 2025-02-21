import datetime
from numbers import Number
from typing import Any, Optional, Annotated

import pydantic

from .. import models
from .models import GameServerStatusBase


def minutes_to_seconds_validator(value: Any) -> Any:
    if isinstance(value, Number):
        # noinspection PyTypeChecker
        return 60 * value
    else:
        return value


class GameServerReport(GameServerStatusBase):
    """游戏服务器上报状态的 schema"""
    day_length: Annotated[Optional[datetime.timedelta], pydantic.BeforeValidator(minutes_to_seconds_validator)] = None
    night_length: Annotated[Optional[datetime.timedelta], pydantic.BeforeValidator(minutes_to_seconds_validator)] = None


class GameServerStatusRead(GameServerStatusBase):
    """请求游戏服务器状态的 schema"""
    model_config = pydantic.ConfigDict(
        json_encoders={
            datetime.timedelta: lambda v: v.total_seconds() / 60,
        }
    )
