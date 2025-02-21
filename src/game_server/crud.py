from typing import Optional, AsyncGenerator, Iterable

import sqlalchemy.exc
import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession

import fastapi_users_with_username

from . import models, schemas, exceptions
from . import status


async def get_game_server(db_session: AsyncSession,
                          game_server_id: int,
                          current_user: Optional[fastapi_users_with_username.models.UP] = None,
                          requires_admin: bool = False,
                          raise_on_not_found: bool = True) -> models.GameServer | None:
    """
    Get a game server by id.
    :param db_session:
    :param game_server_id:
    :param current_user: Only useful when permission_check is True
    :param requires_admin:
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
    if requires_admin:
        if not (current_user.is_superuser or game_server.admin_id == current_user.id):
            raise exceptions.PermissionDenied()
    return game_server


async def get_game_server_by_address(db_session: AsyncSession,
                                     game_server_address: str,
                                     raise_on_not_found: bool = True) -> models.GameServer | None:
    """
    Get a game server by address.
    :param db_session:
    :param game_server_address:
    :param raise_on_not_found:
    :return:
    """
    statement = sqlmodel.select(models.GameServer).where(models.GameServer.address == game_server_address)
    game_server = await db_session.exec(statement)
    try:
        return game_server.one()
    except sqlalchemy.exc.NoResultFound:
        if raise_on_not_found:
            raise exceptions.GameServerNotFound()
        return None


async def create_game_server(db_session: AsyncSession,
                             creator: Optional[fastapi_users_with_username.models.UP],
                             game_server_create: schemas.GameServerCreate,
                             ) -> schemas.GameServerReadAdmin:
    try:
        await get_game_server_by_address(db_session, game_server_create.address)
        raise exceptions.GameServerAlreadyExists("address")
    except exceptions.GameServerNotFound:
        pass
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
        -> Iterable[schemas.GameServerReadAdmin] | Iterable[schemas.GameServerRead]:
    admin = current_user.is_superuser if current_user else False
    statement = sqlmodel.select(models.GameServer).offset(skip).limit(limit)
    game_servers = await db_session.exec(statement)
    return ((schemas.GameServerReadAdmin if admin else schemas.GameServerRead).model_validate(game_server)
            for game_server in game_servers)


async def read_game_server(db_session: AsyncSession,
                           current_user: Optional[fastapi_users_with_username.models.UP],
                           game_server_id: int) \
        -> Optional[schemas.GameServerRead | schemas.GameServerReadAdmin]:
    game_server = await get_game_server(db_session, game_server_id)
    admin = (current_user.is_superuser or game_server.admin_id == current_user.id) if current_user else False
    return (schemas.GameServerReadAdmin if admin else schemas.GameServerRead).model_validate(game_server)


async def update_game_server(db_session: AsyncSession,
                             current_user: Optional[fastapi_users_with_username.models.UP],
                             host: Optional[str],
                             game_server_id: int,
                             game_server_update: schemas.GameServerUpdate) \
        -> Optional[schemas.GameServerReadAdmin]:
    if game_server_update.address:
        try:
            await get_game_server_by_address(db_session, game_server_update.address)
            raise exceptions.GameServerAlreadyExists("address")
        except exceptions.GameServerNotFound:
            pass
    game_server = await get_game_server(db_session, game_server_id)
    if host != game_server.reporter_host and (
            current_user is None or (not current_user.is_superuser and not game_server.admin_id != current_user.id)):
        raise exceptions.PermissionDenied()
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
