from typing import Optional
import fastapi
import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession

import fastapi_users.exceptions

import user.schemas
import user.users
from . import schemas, models


async def get_user_info(db_session: AsyncSession, user_id: str, raise_on_not_found: bool = True):
    """
    Get a user info (no auth info) by id.
    :param db_session:
    :param user_id:
    :param raise_on_not_found:
    :return:
    """
    statement = sqlmodel.select(models.UserInfo).where(models.UserInfo.id == user_id)
    user_info = await db_session.exec(statement)
    if not user_info:
        if raise_on_not_found:
            raise fastapi_users.exceptions.UserNotExists()
        return None
    return user_info.one()


async def create_user_full(db_session: AsyncSession,
                           user_manager: user.users.UserManager,
                           user_full_create: schemas.UserFullCreate,
                           request: Optional[fastapi.Request] = None,
                           ) -> schemas.UserFullReadAdmin:
    """
    Create a user with full information.
    :param db_session:
    :param user_manager:
    :param user_full_create:
    :param request:
    :return:
    """
    info = user_full_create.model_dump()
    user_auth = await user_manager.create(user.schemas.UserCreate.model_validate(info), True, request=request)
    user_id = user_auth.id
    info["id"] = user_id
    user_info_model = models.UserInfo.model_validate(info)
    db_session.add(user_info_model)
    await db_session.commit()
    final_user_info = user_info_model.model_dump() | user_auth.model_dump()
    return schemas.UserFullReadAdmin.model_validate(final_user_info)


async def read_user_full(db_session: AsyncSession,
                         user_manager: user.users.UserManager,
                         user_id: str, ) -> schemas.UserFullRead:
    user_auth = await user_manager.get_safe(user_manager.parse_id(user_id))
    user_info = await get_user_info(db_session, user_id)
    user_info_visibility = models.UserInfoVisibility.model_validate(user_info)
    user_info_visibility_dumped = user_info_visibility.model_dump()
    result = schemas.UserFullRead.model_validate(user_auth.model_dump() | user_info.model_dump())
    for key, value in user_info_visibility_dumped.items():
        if value:
            continue
        field = key[:-7]  # Remove "_public"
        setattr(result, field, None)  # Also works with bool
    return result
