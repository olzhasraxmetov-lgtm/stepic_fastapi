from fastapi import APIRouter, Depends
from starlette import status
from app.core.dependencies import get_current_user
from app.services.progress import ProgressService
from app.models.user import UserORM

progress_router = APIRouter(
    tags=["Мой прогресс"],
)

@progress_router.get('/progress/my')
async def get_my_progress():
    pass

@progress_router.get('courses/{course_id}/progress/')
async def get_my_progress_for_course():
    pass

@progress_router.post('courses/{course_id}/lessons/{lesson_id}/complete')
async def complete_lesson():
    pass

@progress_router.delete('courses/{course_id}/lessons/{lesson_id}/complete}')
async def delete_completion_for_lesson():
    pass
