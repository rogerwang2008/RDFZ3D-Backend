from typing import Optional
import fastapi
from sqlmodel.ext.asyncio.session import AsyncSession

import user.schemas
import user.users
from . import schemas, models


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
