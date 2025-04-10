import enum
import strenum


class ExtendedErrorCode(strenum.UppercaseStrEnum):
    REGISTER_INVALID_USERNAME = enum.auto()


class GeneralCode(strenum.UppercaseStrEnum):
    USER_NOT_FOUND = enum.auto()
    USER_ALREADY_EXISTS = enum.auto()
    INVALID_USERNAME = enum.auto()
    INVALID_PASSWORD = enum.auto()
    WRONG_PASSWORD = enum.auto()

