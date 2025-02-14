from typing import Optional, AsyncGenerator

import fastapi
import sqlalchemy
import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession

import fastapi_users_with_username

from . import models, schemas, exceptions
from . import status


async def get_game_server(db_session: AsyncSession,
                          game_server_id: int,
                          current_user: Optional[fastapi_users_with_username.models.UP] = None,
                          permission_check: bool = False,
                          raise_on_not_found: bool = True) -> models.GameServer | None:
    """
    Get a game server by id.
    :param db_session:
    :param game_server_id:
    :param current_user: Only useful when permission_check is True
    :param permission_check:
    :param raise_on_not_found:
    :return:
    """
    statement = sqlmodel.select(models.GameServer).where(models.GameServer.id == game_server_id)
    game_server = await db_session.exec(statement)
    if not game_server:
        if raise_on_not_found:
            raise exceptions.GameServerNotFound()
        return None
    game_server = game_server.one()
    if permission_check:
        if not (current_user.is_superuser or game_server.admin_id == current_user.id):
            raise exceptions.PermissionDenied()
    return game_server


async def create_game_server(db_session: AsyncSession,
                             creator: Optional[fastapi_users_with_username.models.UP],
                             game_server_create: schemas.GameServerCreate,
                             ) -> schemas.GameServerReadAdmin:
    info = game_server_create.model_dump()
    info["reporter_host"] = str(info["reporter_host"])
    info["admin"] = creator.id if creator else None
    game_server_model = models.GameServer.model_validate(info)
    db_session.add(game_server_model)
    await db_session.commit()
    return schemas.GameServerReadAdmin.model_validate(game_server_model)


async def read_game_servers(db_session: AsyncSession,
                            current_user: Optional[fastapi_users_with_username.models.UP],
                            skip: int = 0, limit: int = 100) \
        -> AsyncGenerator[schemas.GameServerReadAdmin, None] | AsyncGenerator[schemas.GameServerRead, None]:
    admin = current_user.is_superuser if current_user else False
    statement = sqlmodel.select(models.GameServer).offset(skip).limit(limit)
    game_servers = await db_session.exec(statement)
    # return [(schemas.GameServerReadAdmin if admin else schemas.GameServerRead).model_validate(game_server)
    #         for game_server in game_servers]
    # result = []
    for game_server in game_servers:
        admin_result = schemas.GameServerReadAdmin.model_validate(game_server)
        admin_result.status = status.crud.get_server_status(game_server.id)
        # noinspection PyTypeChecker
        yield admin_result if admin else schemas.GameServerRead.model_validate(game_server)


async def read_game_server(db_session: AsyncSession,
                           current_user: Optional[fastapi_users_with_username.models.UP],
                           game_server_id: int) \
        -> Optional[schemas.GameServerRead | schemas.GameServerReadAdmin]:
    game_server = await get_game_server(db_session, game_server_id)
    admin = (current_user.is_superuser or game_server.admin_id == current_user.id) if current_user else False
    # return (schemas.GameServerReadAdmin if admin else schemas.GameServerRead).model_validate(game_server)
    admin_result = schemas.GameServerReadAdmin.model_validate(game_server)
    admin_result.status = status.crud.get_server_status(game_server_id)
    return admin_result if admin else schemas.GameServerRead.model_validate(game_server)


async def update_game_server(db_session: AsyncSession,
                             current_user: Optional[fastapi_users_with_username.models.UP],
                             game_server_id: int,
                             game_server_update: schemas.GameServerUpdate) \
        -> Optional[schemas.GameServerReadAdmin]:
    game_server = await get_game_server(db_session, game_server_id, current_user, True)
    info = game_server_update.model_dump(exclude_unset=True)
    for key, value in info.items():
        setattr(game_server, key, value)
    await db_session.commit()
    return schemas.GameServerReadAdmin.model_validate(game_server)


async def delete_game_server(db_session: AsyncSession,
                             read_user: Optional[fastapi_users_with_username.models.UP],
                             game_server_id: int) -> None:
    game_server = await get_game_server(db_session, game_server_id, read_user, True)
    await db_session.delete(game_server)
    await db_session.commit()
    return None
