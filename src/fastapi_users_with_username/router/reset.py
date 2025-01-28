from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import EmailStr

import fastapi_users
import fastapi_users.router
import fastapi_users.openapi

RESET_PASSWORD_RESPONSES: fastapi_users.openapi.OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": fastapi_users.router.common.ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    fastapi_users.router.common.ErrorCode.RESET_PASSWORD_BAD_TOKEN: {
                        "summary": "Bad or expired token.",
                        "value": {"detail": fastapi_users.router.common.ErrorCode.RESET_PASSWORD_BAD_TOKEN},
                    },
                    fastapi_users.router.common.ErrorCode.RESET_PASSWORD_INVALID_PASSWORD: {
                        "summary": "Password validation failed.",
                        "value": {
                            "detail": {
                                "code": fastapi_users.router.common.ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                                "reason": "Password should be at least 3 characters",
                            }
                        },
                    },
                }
            }
        },
    },
}


def get_reset_password_router(
    get_user_manager: fastapi_users.manager.UserManagerDependency[fastapi_users.models.UP, fastapi_users.models.ID],
) -> APIRouter:
    """Generate a router with the reset password routes."""
    router = APIRouter()

    @router.post(
        "/forgot-password",
        status_code=status.HTTP_202_ACCEPTED,
        name="reset:forgot_password",
    )
    async def forgot_password(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager: fastapi_users.manager.BaseUserManager[fastapi_users.models.UP, fastapi_users.models.ID] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.get_by_email(email)
        except fastapi_users.exceptions.UserNotExists:
            return None

        try:
            await user_manager.forgot_password(user, request)
        except fastapi_users.exceptions.UserInactive:
            pass

        return None

    @router.post(
        "/reset-password",
        name="reset:reset_password",
        responses=RESET_PASSWORD_RESPONSES,
    )
    async def reset_password(
        request: Request,
        token: str = Body(...),
        password: str = Body(...),
        user_manager: fastapi_users.manager.BaseUserManager[fastapi_users.models.UP, fastapi_users.models.ID] = Depends(get_user_manager),
    ):
        try:
            await user_manager.reset_password(token, password, request)
        except (
                fastapi_users.exceptions.InvalidResetPasswordToken,
                fastapi_users.exceptions.UserNotExists,
                fastapi_users.exceptions.UserInactive,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=fastapi_users.router.common.ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        except fastapi_users.exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": fastapi_users.router.common.ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

    return router
