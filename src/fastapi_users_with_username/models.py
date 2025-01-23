from typing import Generic, Optional, Protocol, TypeVar

import fastapi_users.models



class UserProtocol(Protocol[fastapi_users.models.ID]):
    """User protocol that ORM model should follow."""

    id: fastapi_users.models.ID
    username: str
    email: Optional[str]
    phone_no: Optional[str]
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool


UP = TypeVar("UP", bound=UserProtocol)

