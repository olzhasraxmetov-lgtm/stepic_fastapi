from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis import asyncio as redis_asyncio
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache, JsonCoder
from app.api.v1.user import user_router
from app.api.v1.course import course_router
from app.api.v1.purchase import purchase_router
from app.core.config import config
from app.core.logger import setup_logging
from fastapi_limiter import FastAPILimiter
from app.helpers.exception_handler import add_exception_handler

setup_logging()



@asynccontextmanager
async def lifespan(app: FastAPI):
    print('App is starting. Initializing resources')

    redis = redis_asyncio.from_url(config.REDIS_URL)

    try:
        await redis.ping()
        print('Redis connection established')
        FastAPICache.init(
            RedisBackend(redis),
            coder=JsonCoder,
        )
        await FastAPILimiter.init(redis)
        print('FastAPILimiter established')
    except Exception as e:
        print('Redis connection failed:' + str(e))

    yield
    await redis.close()
    print('Redis connection closed')

app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    lifespan=lifespan,
)
add_exception_handler(app)

@app.get('/')
async def root():
    return {'message': 'Hello World'}

app.include_router(user_router)
app.include_router(course_router)
app.include_router(purchase_router)