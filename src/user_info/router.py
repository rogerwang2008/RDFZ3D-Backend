import fastapi
from fastapi import APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

import fastapi_users.exceptions
import fastapi_users.router
import fastapi_users_with_username.exceptions
import fastapi_users_with_username.common
import fastapi_users_with_username.router.common
import user.users, user.utils.dependencies
import universal.database
from . import schemas, crud

router = APIRouter()


# region Register

@router.post(
    "/",
    status_code=fastapi.status.HTTP_201_CREATED,
    responses={
        fastapi.status.HTTP_400_BAD_REQUEST: {
            "model": fastapi_users.router.common.ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        fastapi_users.router.common.ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this username/email/phone_no (provided in detail) already exists.",
                            "value": {
                                "detail": {
                                    "code": fastapi_users.router.common.ErrorCode.REGISTER_USER_ALREADY_EXISTS,
                                    "identifier": fastapi_users_with_username.common.Identifiers.EMAIL,
                                }
                            },
                        },
                        fastapi_users_with_username.router.common.ExtendedErrorCode.REGISTER_INVALID_USERNAME: {
                            "summary": "Username validation failed.",
                            "value": {
                                "detail": {
                                    "code": fastapi_users_with_username.router.common.ExtendedErrorCode.REGISTER_INVALID_USERNAME,
                                    "reason": "Username should be at least 3 characters",
                                }
                            },
                        },
                        fastapi_users.router.common.ErrorCode.REGISTER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": fastapi_users.router.common.ErrorCode.REGISTER_INVALID_PASSWORD,
                                    "reason": "Password should be at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def create_user(user_full: schemas.UserFullCreate,
                      request: fastapi.Request,
                      user_manager: user.users.UserManager = fastapi.Depends(user.users.get_user_manager),
                      db_session: AsyncSession = fastapi.Depends(universal.database.get_async_session),
                      ) -> schemas.UserFullReadAdmin:
    try:
        return await crud.create_user(db_session, user_manager, user_full, request)
    except fastapi_users_with_username.exceptions.UserWithIdentifierAlreadyExists as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "code": fastapi_users.router.common.ErrorCode.REGISTER_USER_ALREADY_EXISTS,
                "identifier": e.identifier,
            }
        )
    except fastapi_users_with_username.exceptions.InvalidUsernameException as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "code": fastapi_users_with_username.router.common.ExtendedErrorCode.REGISTER_INVALID_USERNAME,
                "reason": e.reason,
            }
        )
    except fastapi_users.exceptions.InvalidPasswordException as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "code": fastapi_users.router.common.ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )


# endregion


# region Private

@router.get(
    "/me",
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user"},
    },
)
async def read_user_me(
        user_auth: fastapi_users_with_username.models.UP = fastapi.Depends(
            user.utils.dependencies.get_current_active_user),
        db_session: AsyncSession = fastapi.Depends(universal.database.get_async_session),
) -> schemas.UserFullReadAdmin:
    return await crud.read_user_admin(db_session, user_auth)


# endregion

# region Public

@router.get(
    "/{user_id}",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def read_user(user_id: str,
                    user_manager: user.users.UserManager = fastapi.Depends(user.users.get_user_manager),
                    db_session: AsyncSession = fastapi.Depends(universal.database.get_async_session),
                    ) -> schemas.UserFullRead:
    try:
        return await crud.read_user(db_session, user_manager, user_id)
    except fastapi_users.exceptions.UserNotExists:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

# endregion
