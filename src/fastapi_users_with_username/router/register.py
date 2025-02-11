from typing import Optional

import fastapi
from fastapi import APIRouter, Depends, HTTPException, Request, status

import fastapi_users
import fastapi_users.router

from .. import exceptions, models, schemas, manager, common
from . import common as router_common


def get_register_router(
        get_user_manager: fastapi_users.manager.UserManagerDependency[models.UP, models.ID],
        user_schema: type[schemas.U],
        user_create_schema: type[schemas.UC],
        description: Optional[str] = None,
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register",
        response_model=user_schema,
        status_code=status.HTTP_201_CREATED,
        name="register:register",
        description=description,
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": fastapi_users.router.common.ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            fastapi_users.router.common.ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this username/email/phone_no (provided in detail) already exists.",
                                "value": {
                                    "detail": {
                                        "code": fastapi_users.router.common.ErrorCode.REGISTER_USER_ALREADY_EXISTS,
                                        "identifier": common.Identifiers.EMAIL,
                                    }
                                },
                            },
                            router_common.ExtendedErrorCode.REGISTER_INVALID_USERNAME: {
                                "summary": "Username validation failed.",
                                "value": {
                                    "detail": {
                                        "code": router_common.ExtendedErrorCode.REGISTER_INVALID_USERNAME,
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
    async def register(
            request: Request,
            user_create: user_create_schema,  # type: ignore
            user_manager: manager.BaseUserManager[
                models.UP, models.ID] = Depends(get_user_manager),
    ):
        try:
            created_user = await user_manager.create(
                user_create, safe=True, request=request
            )
        except exceptions.UserWithIdentifierAlreadyExists as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": fastapi_users.router.common.ErrorCode.REGISTER_USER_ALREADY_EXISTS,
                    "identifier": e.identifier,
                }
            )
        except exceptions.InvalidUsernameException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": router_common.ExtendedErrorCode.REGISTER_INVALID_USERNAME,
                    "reason": e.reason,
                }
            )
        except fastapi_users.exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": fastapi_users.router.common.ErrorCode.REGISTER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

        return fastapi_users.schemas.model_validate(user_schema, created_user)

    return router
