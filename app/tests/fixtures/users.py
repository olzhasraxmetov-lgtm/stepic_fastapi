import pytest_asyncio
from sqlalchemy import select
from app.models.user import UserORM
from app.helpers.user_role import UserRoleEnum


@pytest_asyncio.fixture
async def test_author(db_session):
    user = UserORM(
        email="author@example.com",
        username="author_test",
        role=UserRoleEnum.AUTHOR,
        is_active=True,
        full_name="Olzhas Author",
        hashed_password="fake_hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_regular_user(db_session):
    user = UserORM(
        email='regular@example.com',
        username="regular_test",
        role=UserRoleEnum.USER,
        is_active=True,
        full_name="Olzhas Regular User",
        hashed_password="fake_hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db_session):
    """Создает тестового пользователя с ролью ADMIN"""
    user = UserORM(
        email="admin@example.com",
        username="admin_test",
        role=UserRoleEnum.ADMIN,
        is_active=True,
        full_name="Test Admin",
        hashed_password="fake_hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user