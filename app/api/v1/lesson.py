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
from app.core.dependencies import get_course_with_access
lesson_router = APIRouter(
    prefix="/{course_id}/lessons",
)


@lesson_router.get('/', tags=["Lessons"], response_model=list[LessonResponse])
async def get_lessons(
        course: CourseORM = Depends(validation_course_id),
        lessons_service: LessonService = Depends(get_lesson_service),
):
    return await lessons_service.get_all_lessons(course.id)


@lesson_router.post('/', tags=["Lessons"])
async def create_lesson(
        payload: LessonCreate,
        course: CourseORM = Depends(validation_course_id),
        lessons_service: LessonService = Depends(get_lesson_service),
        current_user: UserORM = Depends(get_current_user)
):
    return await lessons_service.create_lesson(payload=payload, current_user=current_user, course=course)

@lesson_router.patch('/{lesson_id}', tags=["Lessons"], response_model=LessonResponse)
async def update_lesson(
        lesson_id: int,
        payload: LessonUpdate,
        course: CourseORM = Depends(get_course_with_access),
        lesson_service: LessonService = Depends(get_lesson_service),
):
    return await lesson_service.update_lesson(payload=payload, course=course, lesson_id=lesson_id)

@lesson_router.delete('/{lesson_id}', tags=["Lessons"], status_code=status.HTTP_200_OK)
async def delete_lesson(
        lesson_id: int,
        course: CourseORM = Depends(get_course_with_access),
        lesson_service: LessonService = Depends(get_lesson_service),
):
    return await lesson_service.delete_lesson(course=course, lesson_id=lesson_id)