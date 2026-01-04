from fastapi import APIRouter, Depends
from starlette import status

from app.core.dependencies import get_course_service
from app.core.dependencies import get_current_user
from app.models.user import UserORM
from app.schemas.course import CourseResponse, CourseCreate
from app.services.course import CourseService

course_router = APIRouter(
    prefix="/course",
    tags=["course"]
)

@course_router.get('/')
async def get_courses():
    return 'Courses'


@course_router.post('/', status_code=status.HTTP_201_CREATED, response_model=CourseResponse)
async def create_course(
        payload: CourseCreate,
        user: UserORM = Depends(get_current_user),
        course_service: CourseService = Depends(get_course_service),
):
    return await course_service.create_course(user, payload)