from typing import Any, Optional

import fastapi_users.exceptions

from . import common


class UserWithIdentifierAlreadyExists(fastapi_users.exceptions.UserAlreadyExists):
    def __init__(self, identifier: Optional[common.Identifiers] = None) -> None:
        self.identifier = identifier


class InvalidUsernameException(fastapi_users.exceptions.FastAPIUsersException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason
