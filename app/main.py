from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.user import user_router
from app.core.config import config
from app.core.logger import setup_logging

from app.helpers.exception_handler import add_exception_handler

setup_logging()

app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION
)

add_exception_handler(app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('App is starting')
    yield
    print('App is stopping')

@app.get('/')
async def root():
    return {'message': 'Hello World'}

app.include_router(user_router)