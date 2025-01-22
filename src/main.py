import contextlib

from fastapi import FastAPI

import user
import universal.database


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    await universal.database.create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.include_router(user.router, prefix="/v1/auth", tags=["auth"])
