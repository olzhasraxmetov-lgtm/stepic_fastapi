from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import config
app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('App is starting')
    yield
    print('App is stopping')

@app.get('/')
async def root():
    return {'message': 'Hello World'}