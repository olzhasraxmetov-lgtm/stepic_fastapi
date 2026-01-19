from loguru import logger

from app.core.exceptions import NotFoundException, ForbiddenException, \
    BadRequestException
from app.models.course import CourseORM
from app.models.user import UserORM
from app.repositories.lesson import LessonRepository
from app.schemas.lesson import LessonCreate, LessonResponse
from app.services.course import CourseService

class LessonService:
    def __init__(self, lesson_repo: LessonRepository):
        self.lesson_repo = lesson_repo


    async def create_lesson(self, course: CourseORM, current_user: UserORM, payload: LessonCreate):
        if course.author_id != current_user.id:
            raise ForbiddenException(
                message='You are not authorized to access this lesson',
                log_message=f'User with {course.author_id} tried to access the course with {course.id}'
            )


        lesson_data = payload.model_dump()
        lesson_data['course_id'] = course.id

        return await self.lesson_repo.create(lesson_data)