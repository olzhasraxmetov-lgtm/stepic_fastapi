from fastapi import APIRouter, Depends, Query
from starlette import status

from app.core.dependencies import get_lesson_service
from app.core.dependencies import get_current_user
from app.models.lesson import LessonORM
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse
from app.services.lesson import LessonService


lesson_router = APIRouter(
    prefix="/lessons",
    tags=["lessons"]
)


@lesson_router.get('/')
async def get_lessons():
    pass