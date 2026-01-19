from fastapi import APIRouter, Depends, Query
from starlette import status

from app.core.dependencies import get_lesson_service
from app.core.dependencies import get_current_user
from app.models.lesson import LessonORM
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse
from app.services.lesson import LessonService
from app.models.user import UserORM
from app.core.dependencies import validation_course_id
from app.models.course import CourseORM

lesson_router = APIRouter(
    prefix="/{course_id}/lessons",
)


@lesson_router.get('/', tags=["Lessons"])
async def get_lessons():
    pass


@lesson_router.post('/', tags=["Lessons"])
async def create_lesson(
        payload: LessonCreate,
        course: CourseORM = Depends(validation_course_id),
        lessons_service: LessonService = Depends(get_lesson_service),
        current_user: UserORM = Depends(get_current_user)
):
    return await lessons_service.create_lesson(payload=payload, current_user=current_user, course=course)