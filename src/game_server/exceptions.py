class GameServerNotFound(Exception):
    pass


class GameServerAlreadyExists(Exception):
    def __init__(self, field: str = "address"):
        self.field = field


class PermissionDenied(Exception):
    pass


class ReporterHostMismatch(Exception):
    pass
