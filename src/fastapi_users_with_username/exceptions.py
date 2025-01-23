from typing import Any

from fastapi_users.exceptions import UserAlreadyExists


class UserWithFieldAlreadyExists(UserAlreadyExists):
    def __init__(self, field: Any = None) -> None:
        self.field = field

