from typing import Type, Optional

import fastapi
import fastapi_users.authentication

from . import schemas, router, models


class FastAPIUsers(fastapi_users.FastAPIUsers[models.UP, fastapi_users.models.ID]):
    def get_register_router(
            self, user_schema: Type[schemas.U], user_create_schema: Type[schemas.UC],
    ) -> fastapi.APIRouter:
        """
        Return a router with a register route.

        :param user_schema: Pydantic schema of a public user.
        :param user_create_schema: Pydantic schema for creating a user.
        :param description: Description to put in doc.
        """
        return router.get_register_router(self.get_user_manager, user_schema, user_create_schema)

    def get_verify_router(self, user_schema: Type[schemas.U]) -> fastapi.APIRouter:
        """
        Return a router with e-mail verification routes.

        :param user_schema: Pydantic schema of a public user.
        """
        return router.get_verify_router(self.get_user_manager, user_schema)

    def get_custom_auth_router(
            self,
            backend: fastapi_users.authentication.AuthenticationBackend,
            user_login_schema: Type[schemas.UL],
            requires_verification: bool = False,
            login_description: Optional[str] = None,
            logout_description: Optional[str] = None,
    ) -> fastapi.APIRouter:
        """
        Return an auth router for a given authentication backend.

        :param backend: The authentication backend instance.
        :param user_login_schema: Pydantic schema for user logging in.
        :param requires_verification: Whether the authentication
        :param login_description: Description to put in login's doc.
        :param logout_description: Description to put in logout's doc.
        require the user to be verified or not. Defaults to False.
        """
        return router.get_auth_router(
            backend,
            self.get_user_manager,
            self.authenticator,
            user_login_schema,
            requires_verification,
            login_description,
            logout_description,
        )

    def get_users_extra_router(
            self,
    ) -> fastapi.APIRouter:
        """
        Return a router only with extra user routes.
        """

        return router.get_users_extra_router(self.get_user_manager, self.authenticator)
