from typing import Any, Optional

from fastapi_users.exceptions import UserAlreadyExists

from . import common

class UserWithIdentifierAlreadyExists(UserAlreadyExists):
    def __init__(self, identifier: Optional[common.Identifiers] = None) -> None:
        self.identifier = identifier

