import contextlib

from fastapi import APIRouter
from . import db, schemas, users

from universal import database
from . import db, schemas, users

router = APIRouter()

# @router.get("/get_user_info", response_model=schemas.User)
router.include_router(
    users.fastapi_users_obj.get_custom_auth_router(users.auth_backend, schemas.UserLogin),
    prefix="",
)

router.include_router(
    users.fastapi_users_obj.get_register_router(schemas.UserRead, schemas.UserCreate),
    prefix="",
)

router.include_router(
    users.fastapi_users_obj.get_verify_router(schemas.UserRead),
    prefix="",
)
router.include_router(
    users.fastapi_users_obj.get_reset_password_router(),
    prefix="",
)
router.include_router(
    users.fastapi_users_obj.get_users_router(schemas.UserRead, schemas.UserUpdate),
    prefix="",
)
