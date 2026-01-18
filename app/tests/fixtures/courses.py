from decimal import Decimal

import pytest_asyncio

from app.models.course import CourseORM


@pytest_asyncio.fixture
async def test_course(db_session, test_author):
    """Создает тестовый неопубликованный курс"""
    course = CourseORM(
        title="Продвинутый FastAPI для продолжающих",
        description="Курс \"Продвинутый FastAPI для продолжающих\" предназначен для разработчиков, которые уже знакомы с основами FastAPI и хотят углубить свои знания",
        price=Decimal("2500.00"),
        author_id=test_author.id,
        is_published=False,
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course


@pytest_asyncio.fixture
async def test_course_published(db_session, test_author):
    """Создает тестовый опубликованный курс"""
    course = CourseORM(
        title="Published Course",
        description="Published Description",
        price=Decimal("200.00"),
        author_id=test_author.id,
        is_published=True,
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course