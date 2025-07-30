import asyncio
import logging
import pathlib
import secrets
from contextlib import asynccontextmanager

import fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from ._router import BaseRouter
from ._repository import BaseRepository


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    yield


@property
def root_router(app: FastAPI):
    return app.router  # noqa

# monkeypatching since app.router is somehow hidden
FastAPI.root_router = root_router  # noqa

app: FastAPI = FastAPI(
    debug=True,
    lifespan=lifespan,
    redirect_slashes=True,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _generate_key() -> str:
    return secrets.token_urlsafe(16)


app.add_middleware(SessionMiddleware, secret_key=_generate_key())


logging.getLogger("uvicorn.error").name = "uvicorn"
