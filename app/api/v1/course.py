from fastapi import APIRouter, Depends
from starlette import status

from app.core.dependencies import get_current_user
from app.core.dependencies import get_course_service
from app.models.course import CourseORM

from app.services.course import CourseService

course_router = APIRouter(
    prefix="/course",
    tags=["course"]
)

@course_router.get('/')
async def get_courses():
    return 'Courses'