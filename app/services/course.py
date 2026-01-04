from loguru import logger

from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException, ForbiddenException, \
    BaseAppException

from app.models.course import CourseORM

from app.repositories.course import CourseRepository

class CourseService:

    def __init__(self, course_repo: CourseRepository):
        self.course_repo = course_repo