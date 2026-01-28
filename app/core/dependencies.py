from collections.abc import AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.database import AsyncSessionLocal
from app.core.exceptions import ForbiddenException
from app.core.exceptions import NotFoundException
from app.models.course import CourseORM
from app.models.user import UserORM
from app.repositories.course import CourseRepository
from app.repositories.lesson import LessonRepository
from app.repositories.purchase import PurchaseRepository
from app.repositories.user import UserRepository
from app.services.course import CourseService
from app.services.lesson import LessonService
from app.services.purchase import PurchaseService
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

async def get_purchase_repository(db: AsyncSession = Depends(get_db)) -> PurchaseRepository:
    return PurchaseRepository(session=db)

async def get_purchase_service(repository: PurchaseRepository = Depends(get_purchase_repository),
                               course_repo: CourseRepository = Depends(get_course_repository)) -> PurchaseService:
    return PurchaseService(purchase_repo=repository,
                           course_repo=course_repo,
                           shop_id=config.YOOKASSA_SHOP_ID,
                           secret_key=config.YOOKASSA_API_SECRET_KEY
                           )

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_service: UserService = Depends(get_user_service)
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

    user = await user_service.repository.get_by_username(username)
    if not user:
        raise credentials_exception
    return user


async def validation_course_id(
        course_id: int,
        course_repo: CourseRepository = Depends(get_course_repository)
):
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise NotFoundException(message="Course not found")
    return course

async def get_course_with_access(
        course: CourseORM = Depends(validation_course_id),
        user: UserORM = Depends(get_current_user)
) -> CourseORM:
    if not (user.is_admin or course.author_id == user.id):
        logger.warning(f'User {user.id} tried to access course {course.id}')
        raise ForbiddenException(message="You don't have permission")
    return course