from fastapi import APIRouter
import fastapi
import fastapi_users_with_username
import fastapi_users_with_username.router


from . import schemas, users, utils, exceptions

router = APIRouter()

_AUTH_LOGIN_ROUTER_DESCRIPTION = """
<b>关于 unique 和 client_type 参数：</b>
<ul>
<li>unique=false 时，仅仅记录 client_type 到这条 token 记录下。</li>
<li>unique=true 时，会使该用户所有相同 client_type 的 token 失效。client_type=null 时则会使该用户所有其他 token 失效。</li>
</ul>
unique 与 client_type 没有关联（unique 不是 client_type 的属性）
"""
router.include_router(
    users.fastapi_users_obj.get_custom_auth_router(users.auth_backend, schemas.UserLogin,
                                                   login_description=_AUTH_LOGIN_ROUTER_DESCRIPTION),
    prefix="",
)
router.include_router(
    users.fastapi_users_obj.get_register_router(schemas.UserRead, schemas.UserCreate),
    prefix="",
    deprecated=True,
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

@router.post(
    "/change-password",
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user"},
        fastapi.status.HTTP_400_BAD_REQUEST: {"description": "Wrong old password"},
    },

)
async def change_password(
        old_password: str = fastapi.Body(..., embed=True),
        new_password: str = fastapi.Body(..., embed=True),
        user_manager: users.UserManager = fastapi.Depends(users.get_user_manager),
        user_auth: fastapi_users_with_username.models.UP = fastapi.Depends(utils.dependencies.get_current_user),
) -> schemas.UserRead:
    try:
        return await user_manager.change_password(user_auth, old_password, new_password)
    except exceptions.WrongPassword:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Wrong old password"
        )
