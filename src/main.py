import contextlib

import fastapi.middleware.cors
import fastapi.staticfiles

import user
import user_info
import game_server
import universal.database, universal.config

from scheduler import scheduler


@contextlib.asynccontextmanager
async def lifespan(_: fastapi.FastAPI):
    await universal.database.create_db_and_tables()
    scheduler.start()
    yield


app = fastapi.FastAPI(
    title=universal.config.settings.PROJECT_NAME,
    description=universal.config.settings.DESCRIPTION,
    version=universal.config.settings.VERSION,
    lifespan=lifespan
)
app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origin_regex=universal.config.settings.ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", fastapi.staticfiles.StaticFiles(directory=universal.config.settings.STATIC_DIR), name="static")
app.mount("/assets", fastapi.staticfiles.StaticFiles(directory=universal.config.settings.ASSETS_DIR), name="assets")


@app.get("/")
async def say_hello(name: str = "World"):
    return {"message": f"Hello {name}!"}


app.include_router(user.router, prefix="/auth", tags=["auth"])
app.include_router(user_info.router, prefix="/user", tags=["User with info"])
app.include_router(game_server.router, prefix="/game_server", tags=["Game server"])
