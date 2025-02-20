import enum
import strenum


class GenderEnum(enum.IntEnum):
    FEMALE = 0
    MALE = 1
    OTHER = 2


class ErrorCode(strenum.UppercaseStrEnum):
    """Better error code. Replacing fastapi_user ones. """
    USER_NOT_FOUND = enum.auto()
    USER_ALREADY_EXISTS = enum.auto()
    INVALID_USERNAME = enum.auto()
    INVALID_PASSWORD = enum.auto()
