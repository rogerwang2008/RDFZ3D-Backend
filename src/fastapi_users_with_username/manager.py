from typing import Optional, Union, Any
import fastapi.security
import fastapi_users
import fastapi_users.jwt
import jwt.exceptions
import ulid
from fastapi import Request

from . import models, db, schemas, common, exceptions


class BaseUserManager(fastapi_users.BaseUserManager[models.UP, fastapi_users.models.ID]):
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
            user_create: schemas.UC,
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
        :raises UserWithIdentifierAlreadyExists: A user already exists with the same e-mail/....
        :return: A new user.
        """
        user_create.username = user_create.username.strip()
        await self.validate_username(user_create.username, user_create)
        await self.validate_password(user_create.password, user_create)

        existing_user_with_username = await self.user_db.get_by_username(user_create.username)
        if existing_user_with_username is not None:
            raise exceptions.UserWithIdentifierAlreadyExists(common.Identifiers.USERNAME)
        if user_create.email:
            existing_user_with_email = await self.user_db.get_by_email(user_create.email)
            if existing_user_with_email is not None:
                raise exceptions.UserWithIdentifierAlreadyExists(common.Identifiers.EMAIL)
        if user_create.phone_no:
            existing_user_with_phone_no = await self.user_db.get_by_phone_no(user_create.phone_no)
            if existing_user_with_phone_no is not None:
                raise exceptions.UserWithIdentifierAlreadyExists(common.Identifiers.PHONE_NO)

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        print(f"User {user_dict} registered")

        await self.on_after_register(created_user, request)

        return created_user

    async def authenticate(
            self, credentials: fastapi.security.OAuth2PasswordRequestForm | schemas.UL,
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

    async def request_verify(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        """
        Start a verification request.

        Triggers the on_after_request_verify handler on success.

        :param user: The user to verify.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserInactive: The user is inactive.
        :raises UserAlreadyVerified: The user is already verified.
        """
        if not user.is_active:
            raise fastapi_users.exceptions.UserInactive()
        if user.is_verified:
            raise fastapi_users.exceptions.UserAlreadyVerified()

        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "aud": self.verification_token_audience,
        }
        token = fastapi_users.jwt.generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )
        await self.on_after_request_verify(user, token, request)

    async def verify(self, token: str, request: Optional[Request] = None) -> models.UP:
        """
        Validate a verification request.

        Changes the is_verified flag of the user to True.

        Triggers the on_after_verify handler on success.

        :param token: The verification token generated by request_verify.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises InvalidVerifyToken: The token is invalid or expired.
        :raises UserAlreadyVerified: The user is already verified.
        :return: The verified user.
        """
        try:
            data = fastapi_users.jwt.decode_jwt(
                token,
                self.verification_token_secret,
                [self.verification_token_audience],
            )
        except jwt.exceptions.PyJWTError:
            raise fastapi_users.exceptions.InvalidVerifyToken()

        try:
            user_id = data["sub"]
            username = data["username"]
        except KeyError:
            raise fastapi_users.exceptions.InvalidVerifyToken()

        try:
            user = await self.get_by_username(username)
        except fastapi_users.exceptions.UserNotExists:
            raise fastapi_users.exceptions.InvalidVerifyToken()

        try:
            parsed_id = self.parse_id(user_id)
        except fastapi_users.exceptions.InvalidID:
            raise fastapi_users.exceptions.InvalidVerifyToken()

        if parsed_id != user.id:
            raise fastapi_users.exceptions.InvalidVerifyToken()

        if user.is_verified:
            raise fastapi_users.exceptions.UserAlreadyVerified()

        verified_user = await self._update(user, {"is_verified": True})

        await self.on_after_verify(verified_user, request)

        return verified_user

    async def update(
            self,
            user_update: schemas.UU,
            user: models.UP,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        """
        Update a user.

        Triggers the on_after_update handler on success

        :param user_update: The UserUpdate model containing
        the changes to apply to the user.
        :param user: The current user to update.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the update, defaults to False
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :return: The updated user.
        """
        if safe:
            updated_user_data = user_update.create_update_dict()
            if "phone_no" in updated_user_data and user.phone_no != updated_user_data["phone_no"]:
                updated_user_data["is_phone_verified"] = False
            if "email" in updated_user_data and user.email != updated_user_data["email"]:
                updated_user_data["is_email_verified"] = False
        else:
            updated_user_data = user_update.create_update_dict_superuser()
        updated_user = await self._update(user, updated_user_data)
        await self.on_after_update(updated_user, updated_user_data, request)
        return updated_user

    async def validate_username(self, username: str, user: Union[schemas.UC, models.UP]) -> None:
        """
        Validate a username.

        *You should overload this method to add your own validation logic.*

        :param username: The username to validate.
        :param user: The user associated to this username.
        :raises InvalidUsernameException: The username is invalid.
        :return: None if the username is valid.
        """
        return


class ULIDIDMixin:
    # noinspection PyMethodMayBeStatic
    def parse_id(self, value: Any) -> ulid.ULID:
        if isinstance(value, ulid.ULID):
            return value
        try:
            return ulid.ULID.parse(value)
        except ValueError as e:
            raise fastapi_users.exceptions.InvalidID() from e
