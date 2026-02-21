from typing import Annotated

from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user, check_course_purchase, valid_lesson
from app.services.lesson_completion import LessonCompletionService
from app.models.user import UserORM
from app.core.dependencies import get_lesson_completion_service
from app.schemas.progress import ProgressResponseMe
from app.models.course import CourseORM
from app.models.lesson import LessonORM

progress_router = APIRouter(
    tags=["Мой прогресс"],
)

@progress_router.get("/{course_id}/progress", response_model=ProgressResponseMe )
async def get_progress(
    # FastAPI сначала проверит, существует ли курс, а потом — куплен ли он
    course: Annotated[CourseORM, Depends(check_course_purchase)],
    user: Annotated[UserORM, Depends(get_current_user)],
    service: LessonCompletionService = Depends(get_lesson_completion_service)
):
    return await service.get_progress_for_course(user.id, course.id)

@progress_router.get('courses/{course_id}/progress/')
async def get_my_progress_for_course():
    pass

@progress_router.post('/courses/{course_id}/lessons/{lesson_id}/complete')
async def complete_lesson(
        lesson: Annotated[LessonORM, Depends(valid_lesson)],
        course: Annotated[CourseORM, Depends(check_course_purchase)],
        user: Annotated[UserORM, Depends(get_current_user)],
        service: LessonCompletionService = Depends(get_lesson_completion_service)
):
    return await service.mark_lesson_as_complete(user_id=user.id, lesson_id=lesson.id, course_id=course.id)

@progress_router.delete('/courses/{course_id}/lessons/{lesson_id}/complete', status_code=204)
async def delete_completion_for_lesson(
        lesson: Annotated[LessonORM, Depends(valid_lesson)],
        course: Annotated[CourseORM, Depends(check_course_purchase)],
        user: Annotated[UserORM, Depends(get_current_user)],
        service: LessonCompletionService = Depends(get_lesson_completion_service)
):
    return await service.mark_lesson_as_complete(user_id=user.id, lesson_id=lesson.id, course_id=course.id)
