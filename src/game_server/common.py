import enum


class GameServerState(enum.StrEnum):
    STOPPED = enum.auto()
    RUNNING = enum.auto()
    MAINTENANCE = enum.auto()
    ACTIVITY = enum.auto()
