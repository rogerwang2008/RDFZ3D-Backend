from typing import Optional

import fastapi.security
from fastapi import Request
import fastapi_users

from . import models
from . import db
from . import exceptions

SECRET = "DONTBEYOURSELFYOUWILLPAYFORIT"


class BaseUserManager(fastapi_users.BaseUserManager[models.UP, fastapi_users.models.ID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    user_db: db.SQLModelUserDatabaseAsync

    async def get_by_username(self, username: str):
        user = await self.user_db.get_by_username(username)
        if user is None:
            raise fastapi_users.exceptions.UserNotExists()
        return user

    async def get_by_phone_no(self, phone_no: str):
        user = await self.user_db.get_by_phone_no(phone_no)
        if user is None:
            raise fastapi_users.exceptions.UserNotExists()
        return user

    async def get_by_any_identifier(self, identifier: str):
        user = await self.user_db.get_by_any_identifier(identifier)
        if user is None:
            raise fastapi_users.exceptions.UserNotExists()
        return user

    async def create(
            self,
            user_create: fastapi_users.schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        """
        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        await self.validate_password(user_create.password, user_create)

        existing_user_with_username = await self.user_db.get_by_username(user_create.username)
        if existing_user_with_username is not None:
            raise exceptions.UserWithFieldAlreadyExists("username")
        if user_create.email:
            existing_user_with_email = await self.user_db.get_by_email(user_create.email)
            if existing_user_with_email is not None:
                raise exceptions.UserWithFieldAlreadyExists("email")
        if user_create.phone_no:
            existing_user_with_phone_no = await self.user_db.get_by_phone_no(user_create.phone_no)
            if existing_user_with_phone_no is not None:
                raise exceptions.UserWithFieldAlreadyExists("phone_no")

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def authenticate(
            self, credentials: fastapi.security.OAuth2PasswordRequestForm
    ) -> Optional[models.UP]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
        try:
            user = await self.get_by_any_identifier(credentials.username)
        except fastapi_users.exceptions.UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user

