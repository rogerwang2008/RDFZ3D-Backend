from typing import Optional

import fastapi

import fastapi_users.authentication, fastapi_users.openapi, fastapi_users.router
from .. import schemas


def get_auth_router(
        backend: fastapi_users.authentication.AuthenticationBackend[fastapi_users.models.UP, fastapi_users.models.ID],
        get_user_manager: fastapi_users.manager.UserManagerDependency[fastapi_users.models.UP, fastapi_users.models.ID],
        authenticator: fastapi_users.authentication.Authenticator[fastapi_users.models.UP, fastapi_users.models.ID],
        user_login_schema: type[schemas.UL],
        requires_verification: bool = False,
        login_description: Optional[str] = None,
        logout_description: Optional[str] = None,
) -> fastapi.APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = fastapi.APIRouter()
    get_current_user_token = authenticator.current_user_token(
        active=True, verified=requires_verification
    )

    login_responses: fastapi_users.openapi.OpenAPIResponseType = {
        fastapi.status.HTTP_400_BAD_REQUEST: {
            "model": fastapi_users.router.common.ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        fastapi_users.router.common.ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials or the user is inactive.",
                            "value": {"detail": fastapi_users.router.common.ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                        fastapi_users.router.common.ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                            "summary": "The user is not verified.",
                            "value": {"detail": fastapi_users.router.common.ErrorCode.LOGIN_USER_NOT_VERIFIED},
                        },
                    }
                }
            },
        },
        **backend.transport.get_openapi_login_responses_success(),
    }

    @router.post(
        "/login",
        name=f"auth:{backend.name}.login",
        responses=login_responses,
        description=login_description,
    )
    async def login(
            request: fastapi.Request,
            credentials: user_login_schema,
            user_manager: fastapi_users.manager.BaseUserManager[fastapi_users.models.UP, fastapi_users.models.ID]
            = fastapi.Depends(get_user_manager),
            strategy: fastapi_users.authentication.Strategy[fastapi_users.models.UP, fastapi_users.models.ID]
            = fastapi.Depends(backend.get_strategy),
    ):
        user = await user_manager.authenticate(credentials)

        if user is None or not user.is_active:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=fastapi_users.router.common.ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if requires_verification and not user.is_verified:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=fastapi_users.router.common.ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
        response = await backend.login(strategy, user)
        await user_manager.on_after_login(user, request, response)
        return response

    logout_responses: fastapi_users.openapi.OpenAPIResponseType = {
        **{
            fastapi.status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user."
            }
        },
        **backend.transport.get_openapi_logout_responses_success(),
    }

    @router.post(
        "/logout", name=f"auth:{backend.name}.logout", responses=logout_responses, description=logout_description
    )
    async def logout(
            user_token: tuple[fastapi_users.models.UP, str] = fastapi.Depends(get_current_user_token),
            strategy: fastapi_users.authentication.Strategy[
                fastapi_users.models.UP, fastapi_users.models.ID] = fastapi.Depends(
                backend.get_strategy),
    ):
        user, token = user_token
        return await backend.logout(strategy, user, token)

    return router
