from typing import Any

from fastapi_users.exceptions import UserAlreadyExists


class UserWithIdentifierAlreadyExists(UserAlreadyExists):
    def __init__(self, identifier: Any = None) -> None:
        self.identifier = identifier

