from typing import Generic, Optional, Protocol, TypeVar

import fastapi_users.models


ID = fastapi_users.models.ID

class UserProtocol(Protocol[ID]):
    """User protocol that ORM model should follow."""

    id: ID
    username: str
    email: Optional[str]
    phone_no: Optional[str]
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    is_email_verified: bool
    is_phone_verified: bool


UP = TypeVar("UP", bound=UserProtocol)

