from typing import Optional
import fastapi
import sqlalchemy.exc
import sqlmodel
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel.ext.asyncio.session import AsyncSession

import fastapi_users.exceptions

import fastapi_users_with_username.models
import user.schemas
import user.users
from . import schemas, models


async def get_user_info(db_session: AsyncSession, user_id: str, raise_on_not_found: bool = True) \
        -> models.UserInfo | None:
    """
    Get a user info (no auth info) by id.
    :param db_session:
    :param user_id:
    :param raise_on_not_found:
    :return:
    """
    statement = sqlmodel.select(models.UserInfo).where(models.UserInfo.id == user_id)
    user_info = await db_session.exec(statement)
    try:
        return user_info.one()
    except sqlalchemy.exc.NoResultFound:
        if raise_on_not_found:
            raise fastapi_users.exceptions.UserNotExists()
        return None


async def create_user(db_session: AsyncSession,
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


async def read_user(db_session: AsyncSession,
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


async def read_user_by_username(db_session: AsyncSession,
                                user_manager: user.users.UserManager,
                                username: str, ) -> schemas.UserFullRead:
    user_auth = await user_manager.get_by_username(username)
    return await read_user(db_session, user_manager, user_auth.id)


async def read_user_by_email(db_session: AsyncSession,
                             user_manager: user.users.UserManager,
                             email: EmailStr) -> schemas.UserFullRead:
    # noinspection PyTypeChecker
    user_auth = await user_manager.get_by_email(email)
    return await read_user(db_session, user_manager, user_auth.id)


async def read_user_by_phone_no(db_session: AsyncSession,
                                user_manager: user.users.UserManager,
                                phone_no: PhoneNumber, ) -> schemas.UserFullRead:
    user_auth = await user_manager.get_by_phone_no(phone_no)
    return await read_user(db_session, user_manager, user_auth.id)


async def read_user_admin(db_session: AsyncSession,
                          user_auth: fastapi_users_with_username.models.UP) -> schemas.UserFullReadAdmin:
    user_info = await get_user_info(db_session, user_auth.id)
    return schemas.UserFullReadAdmin.model_validate(user_auth.model_dump() | user_info.model_dump())


async def read_user_admin_with_id(db_session: AsyncSession,
                                  user_manager: user.users.UserManager,
                                  user_id: str, ) -> schemas.UserFullReadAdmin:
    user_auth = await user_manager.get(user_manager.parse_id(user_id))
    return await read_user_admin(db_session, user_auth)


async def update_user(db_session: AsyncSession,
                      user_manager: user.users.UserManager,
                      user_auth: fastapi_users_with_username.models.UP,
                      user_full_update: schemas.UserFullUpdate,
                      request: Optional[fastapi.Request] = None, ) -> schemas.UserFullReadAdmin:
    updated_user_auth = await user_manager.update(
        user.schemas.UserUpdate.model_validate(user_full_update.model_dump(exclude_unset=True)),
        user_auth, True, request)
    user_info = await get_user_info(db_session, user_auth.id)
    update_info = user_full_update.model_dump(exclude_unset=True)
    for key, value in update_info.items():
        try:
            setattr(user_info, key, value)
        except ValueError:
            continue
    await db_session.commit()
    return schemas.UserFullReadAdmin.model_validate(updated_user_auth.model_dump() | user_info.model_dump())
