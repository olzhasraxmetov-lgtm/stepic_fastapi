from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.v1.step import step_router
from app.core.dependencies import get_course_with_access
from app.core.dependencies import get_lesson_service
from app.core.dependencies import valid_lesson
from app.core.dependencies import validation_course_id
from app.models.course import CourseORM
from app.models.lesson import LessonORM
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse
from app.services.lesson import LessonService

lesson_router = APIRouter(
    prefix="/{course_id}/lessons",
    dependencies=[Depends(validation_course_id)],
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
        course: CourseORM = Depends(get_course_with_access),
        lessons_service: LessonService = Depends(get_lesson_service),
):
    return await lessons_service.create_lesson(payload=payload, course=course)

@lesson_router.patch('/{lesson_id}', tags=["Lessons"], response_model=LessonResponse)
async def update_lesson(
        payload: LessonUpdate,
        course: Annotated[CourseORM, Depends(get_course_with_access)],
        lesson: Annotated[LessonORM, Depends(valid_lesson)],
        lesson_service: Annotated[LessonService, Depends(get_lesson_service)],
):
    return await lesson_service.update_lesson(payload=payload, lesson=lesson)

@lesson_router.delete('/{lesson_id}', tags=["Lessons"], status_code=status.HTTP_200_OK)
async def delete_lesson(
        lesson_id: int,
        course: Annotated[CourseORM, Depends(get_course_with_access)],
        lesson: Annotated[LessonORM, Depends(valid_lesson)],
        lesson_service: LessonService = Depends(get_lesson_service),
):
    return await lesson_service.delete_lesson(lesson=lesson)

lesson_router.include_router(step_router)