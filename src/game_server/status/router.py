import fastapi
from fastapi import APIRouter

import universal.database
from . import crud, schemas
from .. import crud as game_server_crud
from .. import exceptions

router = APIRouter()


@router.post(
    "/report/{game_server_id}",
    description="游戏服务器向此报告状态。如果 15 秒内没有收到报告，则认为服务器 stopped。",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {"description": "UA 不正确"},
        fastapi.status.HTTP_403_FORBIDDEN: {"description": "请求的 Host 与游戏服务器的 reporter_host 不匹配"},
        fastapi.status.HTTP_404_NOT_FOUND: {"description": "未找到 Game Server"},
    },
)
async def report_game_server_status(request: fastapi.Request,
                                    game_server_id: int,
                                    report_body: schemas.GameServerReport,
                                    db_session=fastapi.Depends(universal.database.get_async_session),
                                    ) -> None:
    try:
        game_server = await game_server_crud.get_game_server(db_session, game_server_id)
    except exceptions.GameServerNotFound:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Game server not found")
    if not request.headers.get("User-Agent").startswith("Rdfz3D HTTP Client"):
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                                    detail="Reports should come from Rdfz3D servers")
    if request.client.host != game_server.reporter_host:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="Host mismatch")
    crud.report_server_status(game_server_id, report_body)
