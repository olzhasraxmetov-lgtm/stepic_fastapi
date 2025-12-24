from fastapi import FastAPI
from app.core.config import config

app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION
)

@app.get('/')
async def root():
    return {'message': 'Hello World'}