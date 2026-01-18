import pytest
import asyncio

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from redis.asyncio import from_url
from fastapi_cache import FastAPICache, JsonCoder
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from app.core.database import Base
from app.core.dependencies import get_current_user, get_db
from app.main import app as prod_app

from fastapi_limiter.depends import RateLimiter

async def mock_rate_limiter_call(self, request=None, response=None):
    return None

RateLimiter.__call__ = mock_rate_limiter_call

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

pytest_plugins = [
    "app.tests.fixtures.users",
    "app.tests.fixtures.courses",
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def async_sessionmaker(test_engine):
    return sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture
async def db_session(async_sessionmaker):
    async with async_sessionmaker() as session:
        yield session
        await session.rollback()
        await session.close()



@pytest_asyncio.fixture(scope="session")
async def init_redis():
    """Инициализация Redis и кэша на всю сессию"""
    redis = from_url('redis://localhost:6379/10')
    FastAPICache.init(
        RedisBackend(redis),
        coder=JsonCoder
    )
    await FastAPILimiter.init(redis)
    yield redis
    await redis.close()

@pytest_asyncio.fixture(autouse=True)
async def clear_database(db_session):
    yield
    from app.models.user import UserORM
    from app.models.course import CourseORM
    from sqlalchemy import delete

    await db_session.execute(delete(CourseORM))
    await db_session.execute(delete(UserORM))
    await db_session.commit()

@pytest_asyncio.fixture(scope="session")
async def app_test(async_sessionmaker, init_redis):
    async def _get_db():
        async with async_sessionmaker() as session:
            try:
                yield session
            finally:
                await session.rollback()

    prod_app.dependency_overrides[get_db] = _get_db
    yield prod_app
    prod_app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def clear_cache(init_redis):
    """Фикстура для ручной или автоматической очистки кэша"""
    await init_redis.flushdb()
    yield


@pytest_asyncio.fixture
async def client(app_test: FastAPI, test_author, clear_cache):
    app_test.dependency_overrides[get_current_user] = lambda: test_author
    async with AsyncClient(
            transport=ASGITransport(app=app_test),
            base_url="http://testserver"
    ) as c:
        yield c

    app_test.dependency_overrides.pop(get_current_user, None)

@pytest_asyncio.fixture
async def user_client(app_test: FastAPI, test_regular_user):
    app_test.dependency_overrides[get_current_user] = lambda: test_regular_user

    async with AsyncClient(transport=ASGITransport(app=app_test), base_url="http://testserver") as c:
        yield c

    app_test.dependency_overrides.pop(get_current_user, None)


#@pytest_asyncio.fixture
# async def limiter_client(app_test: FastAPI, test_author):
#     """Специальный клиент для теста лимитов, где RateLimiter РАБОТАЕТ"""
#     app_test.dependency_overrides[get_current_user] = lambda: test_author
#
#     async with AsyncClient(transport=ASGITransport(app=app_test), base_url="http://testserver") as c:
#         yield c
#
#     app_test.dependency_overrides.pop(get_current_user, None)