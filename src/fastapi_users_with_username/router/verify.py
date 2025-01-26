import fastapi
import fastapi_users
from fastapi_users.router.common import ErrorCode, ErrorModel
from ..manager import BaseUserManager


def get_verify_router(
        get_user_manager: fastapi_users.manager.UserManagerDependency[fastapi_users.models.UP, fastapi_users.models.ID],
        user_schema: type[fastapi_users.schemas.U],
):
    router = fastapi.APIRouter()

    @router.post(
        "/request-verify-token",
        status_code=fastapi.status.HTTP_202_ACCEPTED,
        name="verify:request-token",
    )
    async def request_verify_token(
            request: fastapi.Request,
            username: str = fastapi.Body(..., embed=True),
            user_manager: BaseUserManager[fastapi_users.models.UP, fastapi_users.models.ID] = fastapi.Depends(
                get_user_manager),
    ):
        try:
            user = await user_manager.get_by_username(username)
            await user_manager.request_verify(user, request)
        except (
                fastapi_users.exceptions.UserNotExists,
                fastapi_users.exceptions.UserInactive,
                fastapi_users.exceptions.UserAlreadyVerified,
        ):
            pass

        return None

    @router.post(
        "/verify",
        response_model=user_schema,
        name="verify:verify",
        responses={
            fastapi.status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.VERIFY_USER_BAD_TOKEN: {
                                "summary": "Bad token, not existing user or"
                                           "not the e-mail currently set for the user.",
                                "value": {"detail": ErrorCode.VERIFY_USER_BAD_TOKEN},
                            },
                            ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                                "summary": "The user is already verified.",
                                "value": {
                                    "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                                },
                            },
                        }
                    }
                },
            }
        },
    )
    async def verify(
            request: fastapi.Request,
            token: str = fastapi.Body(..., embed=True),
            user_manager: BaseUserManager[fastapi_users.models.UP, fastapi_users.models.ID] = fastapi.Depends(
                get_user_manager),
    ):
        try:
            user = await user_manager.verify(token, request)
            return fastapi_users.schemas.model_validate(user_schema, user)
        except (fastapi_users.exceptions.InvalidVerifyToken, fastapi_users.exceptions.UserNotExists):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )
        except fastapi_users.exceptions.UserAlreadyVerified:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
            )

    return router
