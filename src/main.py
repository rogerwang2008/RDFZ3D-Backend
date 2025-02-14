import contextlib

from fastapi import FastAPI

import user
import game_server
import universal.database, universal.config

from scheduler import scheduler


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    await universal.database.create_db_and_tables()
    scheduler.start()
    yield


app = FastAPI(
    title=universal.config.settings.PROJECT_NAME,
    description=universal.config.settings.DESCRIPTION,
    version=universal.config.settings.VERSION,
    lifespan=lifespan
)


@app.get("/")
async def say_hello(name: str = "World"):
    return {"message": f"Hello {name}!"}


app.include_router(user.router, prefix="/auth", tags=["auth"])
app.include_router(game_server.router, prefix="/game_server", tags=["Game server"])
