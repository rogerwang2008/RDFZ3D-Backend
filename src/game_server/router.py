from typing import Optional
import aiostream
import fastapi
from fastapi import APIRouter

import fastapi_users_with_username
import universal.database
import user.utils
from . import crud, exceptions, schemas
from . import status

router = APIRouter()

router.include_router(status.router)

@router.post("/", status_code=fastapi.status.HTTP_201_CREATED)
async def create_game_server(
        game_server: schemas.GameServerCreate,
        current_user: Optional[fastapi_users_with_username.models.UP] = fastapi.Depends(
            user.utils.get_current_active_verified_user_optional),
        db_session=fastapi.Depends(universal.database.get_async_session),
) -> schemas.GameServerReadAdmin:
    print(current_user)
    return await crud.create_game_server(db_session, current_user, game_server)


@router.get("/")
async def get_game_servers(
        skip: int = fastapi.Query(default=0, ge=0, description="跳过前_个"),
        limit: int = fastapi.Query(default=100, ge=1, description="返回_个"),
        current_user: Optional[fastapi_users_with_username.models.UP] = fastapi.Depends(
            user.utils.get_current_active_verified_user_optional),
        db_session=fastapi.Depends(universal.database.get_async_session),
) -> list[schemas.GameServerRead] | list[schemas.GameServerReadAdmin]:
    return await aiostream.stream.list(crud.read_game_servers(db_session, current_user, skip, limit))


@router.get(
    "/{game_server_id}",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {"description": "Game server not found"},
    },
)
async def get_game_server(
        game_server_id: int,
        current_user: Optional[fastapi_users_with_username.models.UP] = fastapi.Depends(
            user.utils.get_current_active_verified_user_optional),
        db_session=fastapi.Depends(universal.database.get_async_session),
) -> schemas.GameServerRead | schemas.GameServerReadAdmin:
    try:
        return await crud.read_game_server(db_session, current_user, game_server_id)
    except exceptions.GameServerNotFound:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Game server not found")


@router.patch("/{game_server_id}")
async def update_game_server(
        game_server_id: int,
        game_server: schemas.GameServerUpdate,
        current_user: Optional[fastapi_users_with_username.models.UP] = fastapi.Depends(
            user.utils.get_current_active_verified_user_optional),
        db_session=fastapi.Depends(universal.database.get_async_session),
) -> schemas.GameServerReadAdmin:
    try:
        return await crud.update_game_server(db_session, current_user, game_server_id, game_server)
    except exceptions.GameServerNotFound:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Game server not found")
    except exceptions.PermissionDenied:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="Not the admin or superuser")


@router.delete("/{game_server_id}")
async def delete_game_server(
        game_server_id: int,
        current_user: Optional[fastapi_users_with_username.models.UP] = fastapi.Depends(
            user.utils.get_current_active_verified_user_optional),
        db_session=fastapi.Depends(universal.database.get_async_session),
) -> None:
    try:
        await crud.delete_game_server(db_session, current_user, game_server_id)
    except exceptions.GameServerNotFound:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Game server not found")
    except exceptions.PermissionDenied:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="Not the admin or superuser")
