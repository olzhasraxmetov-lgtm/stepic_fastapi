from collections.abc import AsyncGenerator
from typing import Annotated

import jwt
import redis.asyncio as redis_asyncio
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.database import AsyncSessionLocal
from app.core.exceptions import ForbiddenException
from app.core.exceptions import NotFoundException
from app.core.websocket_manager import ConnectionManager
from app.core.websocket_manager import manager
from app.helpers.user_role import UserRoleEnum
from app.models.course import CourseORM
from app.models.lesson import LessonORM
from app.models.step import StepORM
from app.models.user import UserORM
from app.repositories.comment import CommentRepository
from app.repositories.course import CourseRepository
from app.repositories.lesson import LessonRepository
from app.repositories.purchase import PurchaseRepository
from app.repositories.reaction import ReactionRepository
from app.repositories.progress import ProgressRepository
from app.repositories.step import StepRepository
from app.repositories.user import UserRepository
from app.services.comment import CommentService
from app.services.course import CourseService
from app.services.lesson import LessonService
from app.services.notification import NotificationService
from app.services.purchase import PurchaseService
from app.services.reaction import ReactionService
from app.services.step import StepService
from app.services.user import UserService
from app.services.progress import ProgressService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

DBSession = Annotated[AsyncSession, Depends(get_db)]

async def get_redis():
    client = redis_asyncio.from_url(config.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()

async def service_http_user_id(request: Request):
    return request.client.host

async def get_user_service(db: DBSession) -> UserService:
    return UserService(repository=UserRepository(session=db))

async def get_course_service(db: DBSession) -> CourseService:
    return CourseService(course_repo=CourseRepository(session=db))

async def get_lesson_repository(db: AsyncSession = Depends(get_db)) -> LessonRepository:
    return LessonRepository(session=db)

async def get_lesson_service(db: DBSession) -> LessonService:
    return LessonService(lesson_repo=LessonRepository(session=db), purchase_repo=PurchaseRepository(session=db))

async def get_step_service(db: DBSession) -> StepService:
    return StepService(step_repo=StepRepository(session=db), purchase_repo=PurchaseRepository(session=db))

async def get_purchase_service(
        db: DBSession
):
    return PurchaseService(
        purchase_repo=PurchaseRepository(session=db),
        course_repo=CourseRepository(session=db),
        shop_id=config.YOOKASSA_SHOP_ID,
        secret_key=config.YOOKASSA_API_SECRET_KEY
    )

def get_ws_manager():
    return manager


async def get_notification_service(
    redis: Redis = Depends(get_redis),
    ws_manager: ConnectionManager = Depends(get_ws_manager)
) -> NotificationService:
    return NotificationService(redis, ws_manager)

async def get_comment_service(db: DBSession, notification_service = Depends(get_notification_service),) -> CommentService:
    step_repo = StepRepository(session=db)
    purchase_repo = PurchaseRepository(session=db)

    step_service = StepService(step_repo=step_repo, purchase_repo=purchase_repo)

    comment_repo = CommentRepository(session=db)

    return CommentService(comment_repo=comment_repo, step_service=step_service, notification_service=notification_service)


async def get_progress_service(db: DBSession) -> ProgressService:
    return ProgressService(progress_repo=ProgressRepository(session=db))



async def get_reaction_service(
        db: DBSession,
        comment_service: CommentService = Depends(get_comment_service),
        notification_service = Depends(get_notification_service),
) -> ReactionService:
    return ReactionService(
        reaction_repository=ReactionRepository(session=db),
        comment_service=comment_service,
        notification_service=notification_service
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
        db: DBSession
):
    course = await CourseRepository(session=db).get_by_id(course_id)
    if not course:
        raise NotFoundException(message="Course not found")
    return course

async def get_course_with_access(
        course: Annotated[CourseORM, Depends(validation_course_id)],
        user: Annotated[UserORM, Depends(get_current_user)],
) -> CourseORM:
    if not (user.role == UserRoleEnum.ADMIN or course.author_id == user.id):
        logger.warning(f'User {user.id} tried to access course {course.id}')
        raise ForbiddenException(message="You don't have permission")
    return course

async def valid_lesson(
        lesson_id: int,
        course: Annotated[CourseORM, Depends(validation_course_id)],
        db: DBSession
) -> LessonORM:
    repo = LessonRepository(db)
    lesson = await repo.get_lesson_with_course(lesson_id)

    if not lesson or lesson.course_id != course.id:
        raise NotFoundException(message=f"Lesson {lesson_id} not found in course {course.id}")

    return lesson

async def valid_step(
        step_id: int,
        lesson: Annotated[LessonORM, Depends(valid_lesson)],
        db: DBSession
) -> StepORM:
    repo = StepRepository(db)
    step = await repo.get_by_id(step_id)
    if not step or step.lesson_id != lesson.id:
        raise NotFoundException(message=f"Step {step_id} not found in lesson {lesson.id}")
    return step