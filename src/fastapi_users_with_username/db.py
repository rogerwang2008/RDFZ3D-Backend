import typing
import uuid
from typing import Optional

from pydantic import UUID4, EmailStr
import sqlmodel
from sqlalchemy import func
import fastapi_users_db_sqlmodel


class SQLModelBaseUserDB(fastapi_users_db_sqlmodel.SQLModelBaseUserDB):
    id: UUID4 = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    username: str = sqlmodel.Field(
        sa_column_kwargs={"unique": True, "index": True}, nullable=False
    )
    if typing.TYPE_CHECKING:  # pragma: no cover
        email: Optional[str]
    else:
        email: Optional[EmailStr] = sqlmodel.Field(
            sa_column_kwargs={"unique": True, "index": True}, nullable=True
        )
    phone_no: Optional[str] = sqlmodel.Field(
        sa_column_kwargs={"unique": True, "index": True}, nullable=True
    )
    is_active: bool = sqlmodel.Field(True, nullable=False)
    is_superuser: bool = sqlmodel.Field(False, nullable=False)
    is_verified: bool = sqlmodel.Field(False, nullable=False)


class SQLModelUserDatabaseAsync(fastapi_users_db_sqlmodel.SQLModelUserDatabaseAsync):
    async def get_by_phone_no(self, phone_no: str):
        """Get a single user by phone number."""
        statement = sqlmodel.select(self.user_model).where(
            self.user_model.phone_no == phone_no
        )
        results = await self.session.execute(statement)
        obj = results.first()
        if obj is None:
            return None
        return obj[0]

    async def get_by_username(self, username: str):
        """Get a single user by username."""
        statement = sqlmodel.select(self.user_model).where(
            func.lower(self.user_model.username) == func.lower(username)
        )
        results = await self.session.execute(statement)
        obj = results.first()
        if obj is None:
            return None
        return obj[0]

    async def get_by_any_identifier(self, identifier: str):
        """Get a single user by username or email or phone number."""
        statement = sqlmodel.select(self.user_model).where(
            (func.lower(self.user_model.username) == func.lower(identifier))
            | (func.lower(self.user_model.email) == func.lower(identifier))
            | (self.user_model.phone_no == identifier)
        )
        results = await self.session.execute(statement)
        obj = results.first()
        if obj is None:
            return None
        return obj[0]
