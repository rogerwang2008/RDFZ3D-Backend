from typing import Optional

import fastapi
import sqlalchemy
import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession

import fastapi_users_with_username

from . import models, schemas, exceptions


async def create_game_server(db_session: AsyncSession,
                             creator: Optional[fastapi_users_with_username.models.UP],
                             game_server: schemas.GameServerCreate,
                             ) -> schemas.GameServerReadAdmin:
    game_server_dumped = game_server.model_dump()
    game_server_dumped["reporter_host"] = str(game_server_dumped["reporter_host"])
    game_server_dumped["admin"] = creator.id if creator else None
    game_server_model = models.GameServer.model_validate(game_server_dumped)
    db_session.add(game_server_model)
    await db_session.commit()
    return schemas.GameServerReadAdmin.model_validate(game_server_model)


async def read_game_servers(db_session: AsyncSession,
                            read_user: Optional[fastapi_users_with_username.models.UP],
                            skip: int = 0, limit: int = 100) \
        -> list[schemas.GameServerRead] | list[schemas.GameServerReadAdmin]:
    admin = read_user.is_superuser if read_user else False
    statement = sqlmodel.select(models.GameServer).offset(skip).limit(limit)
    game_servers = await db_session.exec(statement)
    return [(schemas.GameServerReadAdmin if admin else schemas.GameServerRead).model_validate(game_server)
            for game_server in game_servers]


async def read_game_server(db_session: AsyncSession,
                           read_user: Optional[fastapi_users_with_username.models.UP],
                           game_server_id: int, admin: bool = False) \
        -> Optional[schemas.GameServerRead | schemas.GameServerReadAdmin]:
    statement = sqlmodel.select(models.GameServer).where(models.GameServer.id == game_server_id)
    game_server = await db_session.exec(statement)
    if not game_server:
        return None
    game_server = game_server.one()
    admin = (read_user.is_superuser or game_server.admin == read_user.id) if read_user else False
    return (schemas.GameServerReadAdmin if admin else schemas.GameServerRead).model_validate(game_server)
