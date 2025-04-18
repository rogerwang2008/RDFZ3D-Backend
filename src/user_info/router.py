import PIL
import fastapi
from fastapi import APIRouter
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel.ext.asyncio.session import AsyncSession

import fastapi_users.exceptions
import fastapi_users.router
import fastapi_users_with_username.exceptions
import fastapi_users_with_username.common
import fastapi_users_with_username.router.common
import user.users
import user.utils
import universal.database
from . import schemas, crud

router = APIRouter()

HTTP_400_DOC = {
    "model": fastapi_users.router.common.ErrorModel,
    "content": {
        "application/json": {
            "examples": {
                fastapi_users_with_username.router.common.GeneralCode.USER_ALREADY_EXISTS: {
                    "summary": "A user with this username/email/phone_no (provided in detail) already exists.",
                    "value": {
                        "detail": {
                            "code": fastapi_users_with_username.router.common.GeneralCode.USER_ALREADY_EXISTS,
                            "identifier": fastapi_users_with_username.common.Identifiers.EMAIL,
                        }
                    },
                },
                fastapi_users_with_username.router.common.GeneralCode.INVALID_USERNAME: {
                    "summary": "Username validation failed.",
                    "value": {
                        "detail": {
                            "code": fastapi_users_with_username.router.common.GeneralCode.INVALID_USERNAME,
                            "reason": "Username should be at least 3 characters",
                        }
                    },
                },
                fastapi_users_with_username.router.common.GeneralCode.INVALID_PASSWORD: {
                    "summary": "Password validation failed.",
                    "value": {
                        "detail": {
                            "code": fastapi_users_with_username.router.common.GeneralCode.INVALID_PASSWORD,
                            "reason": "Password should be at least 3 characters",
                        }
                    },
                },
            }
        }
    },
}


# region Register

@router.post(
    "/register",
    status_code=fastapi.status.HTTP_201_CREATED,
    responses={
        fastapi.status.HTTP_400_BAD_REQUEST: HTTP_400_DOC
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
                "code": fastapi_users_with_username.router.common.GeneralCode.USER_ALREADY_EXISTS,
                "identifier": e.identifier,
            }
        )
    except fastapi_users_with_username.exceptions.InvalidUsernameException as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "code": fastapi_users_with_username.router.common.GeneralCode.INVALID_USERNAME,
                "reason": e.reason,
            }
        )
    except fastapi_users.exceptions.InvalidPasswordException as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "code": fastapi_users_with_username.router.common.GeneralCode.INVALID_PASSWORD,
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


@router.patch(
    "/me",
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user"},
        fastapi.status.HTTP_400_BAD_REQUEST: HTTP_400_DOC,
    },
)
async def update_user_me(
        user_update: schemas.UserFullUpdate,
        request: fastapi.Request,
        user_manager: user.users.UserManager = fastapi.Depends(user.users.get_user_manager),
        user_auth: fastapi_users_with_username.models.UP = fastapi.Depends(
            user.utils.dependencies.get_current_active_user),
        db_session: AsyncSession = fastapi.Depends(universal.database.get_async_session),
) -> schemas.UserFullReadAdmin:
    try:
        return await crud.update_user(db_session, user_manager, user_auth, user_update, True, request)
    except fastapi_users_with_username.exceptions.UserWithIdentifierAlreadyExists as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "code": fastapi_users_with_username.router.common.GeneralCode.USER_ALREADY_EXISTS,
                "identifier": e.identifier,
            }
        )
    except fastapi_users_with_username.exceptions.InvalidUsernameException as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "code": fastapi_users_with_username.router.common.GeneralCode.INVALID_USERNAME,
                "reason": e.reason,
            }
        )
    except fastapi_users.exceptions.InvalidPasswordException as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "code": fastapi_users_with_username.router.common.GeneralCode.INVALID_PASSWORD,
                "reason": e.reason,
            },
        )


@router.post(
    "/upload_avatar",
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user"},
        fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"description": "Unsupported media type"},
    },
)
async def upload_avatar(
        user_manager: user.users.UserManager = fastapi.Depends(user.users.get_user_manager),
        user_auth: fastapi_users_with_username.models.UP = fastapi.Depends(
            user.utils.dependencies.get_current_active_user),
        avatar_file: fastapi.UploadFile = fastapi.File(...),
        db_session: AsyncSession = fastapi.Depends(universal.database.get_async_session),
) -> None:
    try:
        return await crud.upload_avatar(db_session, user_manager, user_auth, avatar_file.file, avatar_file.content_type)
    except PIL.UnidentifiedImageError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported image type",
        )


# endregion

# region Public

@router.get(
    "/{user_id}",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "Inactive user"},
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
    except fastapi_users.exceptions.UserInactive:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )


@router.get(
    "/get_by_username/{username}",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "Inactive user"},
    },
)
async def read_user_by_username(username: str,
                                user_manager: user.users.UserManager = fastapi.Depends(user.users.get_user_manager),
                                db_session: AsyncSession = fastapi.Depends(universal.database.get_async_session),
                                ) -> schemas.UserFullRead:
    try:
        return await crud.read_user_by_username(db_session, user_manager, username)
    except fastapi_users.exceptions.UserNotExists:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except fastapi_users.exceptions.UserInactive:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )


@router.get(
    "/get_by_email/{email}",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "Inactive user"},
    },
)
async def read_user_by_username(email: EmailStr,
                                user_manager: user.users.UserManager = fastapi.Depends(user.users.get_user_manager),
                                db_session: AsyncSession = fastapi.Depends(universal.database.get_async_session),
                                ) -> schemas.UserFullRead:
    try:
        return await crud.read_user_by_email(db_session, user_manager, email)
    except fastapi_users.exceptions.UserNotExists:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except fastapi_users.exceptions.UserInactive:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )


@router.get(
    "/get_by_phone_no/{phone_no}",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "Inactive user"},
    },
)
async def read_user_by_phone_number(phone_no: PhoneNumber,
                                    user_manager: user.users.UserManager = fastapi.Depends(user.users.get_user_manager),
                                    db_session: AsyncSession = fastapi.Depends(universal.database.get_async_session),
                                    ) -> schemas.UserFullRead:
    try:
        return await crud.read_user_by_phone_no(db_session, user_manager, phone_no)
    except fastapi_users.exceptions.UserNotExists:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except fastapi_users.exceptions.UserInactive:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

# endregion
