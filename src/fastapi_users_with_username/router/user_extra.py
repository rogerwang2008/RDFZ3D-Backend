import fastapi
import fastapi_users.manager

from .. import manager, exceptions
from . import common


def get_users_extra_router(
        get_user_manager: fastapi_users.manager.UserManagerDependency,
        authenticator: fastapi_users.fastapi_users.Authenticator,
) -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    get_current_user = authenticator.current_user(
        active=False, verified=False
    )

    @router.post(
        "/change-password",
        status_code=fastapi.status.HTTP_204_NO_CONTENT,
        responses={
            fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user"},
            fastapi.status.HTTP_400_BAD_REQUEST: {"description": "Wrong old password"},
        },

    )
    async def change_password(
            old_password: str = fastapi.Body(..., embed=True),
            new_password: str = fastapi.Body(..., embed=True),
            user_manager: manager.BaseUserManager = fastapi.Depends(get_user_manager),
            user_auth: fastapi_users.models.UP = fastapi.Depends(get_current_user),
    ) -> None:
        try:
            return await user_manager.change_password(user_auth, old_password, new_password)
        except exceptions.WrongPassword:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=common.GeneralCode.WRONG_PASSWORD
            )
        except fastapi_users.exceptions.InvalidPasswordException:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=common.GeneralCode.INVALID_PASSWORD
            )

    return router
