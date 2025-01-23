from typing import Optional

from fastapi import Request
import fastapi_users

from . import models
from .db import SQLModelUserDatabaseAsync
from .exceptions import UserWithFieldAlreadyExists

SECRET = "DONTBEYOURSELFYOUWILLPAYFORIT"


class BaseUserManager(fastapi_users.BaseUserManager[models.UPwUN, fastapi_users.models.ID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    user_db: SQLModelUserDatabaseAsync

    async def create(
            self,
            user_create: fastapi_users.schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UPwUN:
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

        # existing_user = ((await self.user_db.get_by_email(user_create.email) if user_create.email else None)
        #                  or (await self.user_db.get_by_phone_no(user_create.phone_no) if user_create.phone_no else None)
        #                  or await self.user_db.get_by_username(user_create.username))
        # if existing_user is not None:
        #     raise fastapi_users.exceptions.UserAlreadyExists()
        existing_user_with_username = await self.user_db.get_by_username(user_create.username)
        if existing_user_with_username is not None:
            raise UserWithFieldAlreadyExists("username")
        if user_create.email:
            existing_user_with_email = await self.user_db.get_by_email(user_create.email)
            if existing_user_with_email is not None:
                raise UserWithFieldAlreadyExists("email")
        if user_create.phone_no:
            existing_user_with_phone_no = await self.user_db.get_by_phone_no(user_create.phone_no)
            if existing_user_with_phone_no is not None:
                raise UserWithFieldAlreadyExists("phone_no")

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
