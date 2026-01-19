from collections.abc import AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.database import AsyncSessionLocal
from app.models.user import UserORM
from app.repositories.course import CourseRepository
from app.repositories.lesson import LessonRepository
from app.repositories.user import UserRepository
from app.services.course import CourseService
from app.services.lesson import LessonService
from app.services.user import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

async def service_http_user_id(request: Request):
    return request.client.host

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session=db)

async def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository=repository)

async def get_course_repository(db: AsyncSession = Depends(get_db)) -> CourseRepository:
    return CourseRepository(session=db)

async def get_course_service(repository: CourseRepository = Depends(get_course_repository)) -> CourseService:
    return CourseService(course_repo=repository)

async def get_lesson_repository(db: AsyncSession = Depends(get_db)) -> LessonRepository:
    return LessonRepository(session=db)

async def get_lesson_service(repository: LessonRepository = Depends(get_lesson_repository)) -> LessonService:
    return LessonService(lesson_repo=repository)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_service: UserService = Depends(get_user_service)  # Используем уже готовый сервис
) -> UserORM:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("username")
        if not username:
            raise credentials_exception
    except (jwt.PyJWTError, jwt.ExpiredSignatureError):
        raise credentials_exception

    # Делегируем поиск пользователя сервису
    user = await user_service.repository.get_by_username(username)
    if not user:
        raise credentials_exception
    return user




