from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.services.lesson_completion import LessonCompletionService
from app.models.user import UserORM
from app.core.dependencies import get_lesson_completion_service

progress_router = APIRouter(
    tags=["Мой прогресс"],
)

@progress_router.get('/progress/my')
async def get_my_progress():
    pass

@progress_router.get('courses/{course_id}/progress/')
async def get_my_progress_for_course():
    pass

@progress_router.post('/courses/{course_id}/lessons/{lesson_id}/complete')
async def complete_lesson(
        course_id: int,
        lesson_id: int,
        user: UserORM = Depends(get_current_user),
        progress_service: LessonCompletionService = Depends(get_lesson_completion_service),
):
    return await progress_service.mark_lesson_as_complete(user_id=user.id, lesson_id=lesson_id, course_id=course_id)

@progress_router.delete('/courses/{course_id}/lessons/{lesson_id}/complete')
async def delete_completion_for_lesson():
    pass
