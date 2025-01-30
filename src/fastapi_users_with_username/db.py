from typing import TYPE_CHECKING, Optional

import fastapi_users_db_sqlmodel.access_token
import sqlalchemy.sql.schema
import ulid

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
import sqlmodel
from sqlalchemy import func
import fastapi_users_db_sqlmodel

PhoneNumber.default_region_code = "CN"
PhoneNumber.phone_format = "E164"


class SQLModelBaseUserDB(sqlmodel.SQLModel):
    __tablename__ = "user"
    # noinspection PyTypeChecker
    id: str = sqlmodel.Field(default_factory=ulid.ULID, primary_key=True, nullable=False, min_length=26, max_length=26,
                             sa_type=sqlalchemy.CHAR(26))
    username: str = sqlmodel.Field(regex=r"^[a-zA-Z0-9_-]+$", unique=True, index=True, nullable=False)
    if TYPE_CHECKING:
        email: Optional[str]
    else:
        email: Optional[EmailStr] = sqlmodel.Field(unique=True, index=True, nullable=True)
    if TYPE_CHECKING:
        phone_no: Optional[str]
    else:
        phone_no: Optional[PhoneNumber] = sqlmodel.Field(unique=True, index=True, nullable=True)
    hashed_password: str
    is_active: bool = sqlmodel.Field(True, nullable=False)
    is_superuser: bool = sqlmodel.Field(False, nullable=False)
    is_verified: bool = sqlmodel.Field(False, nullable=False)
    is_email_verified: bool = sqlmodel.Field(False, nullable=False)
    is_phone_verified: bool = sqlmodel.Field(False, nullable=False)

    class Config:
        orm_mode = True


class SQLModelBaseAccessToken(fastapi_users_db_sqlmodel.access_token.SQLModelBaseAccessToken):
    # noinspection PyTypeChecker
    user_id: str = sqlmodel.Field(foreign_key="user.id", nullable=False, sa_type=sqlalchemy.CHAR(26))


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
