from typing import Type

import fastapi
import fastapi_users

from . import schemas, router, models


class FastAPIUsers(fastapi_users.FastAPIUsers[models.UP, fastapi_users.models.ID]):
    def get_verify_router(self, user_schema: Type[schemas.U]) -> fastapi.APIRouter:
        """
        Return a router with e-mail verification routes.

        :param user_schema: Pydantic schema of a public user.
        """
        return router.verify.get_verify_router(self.get_user_manager, user_schema)
