from loguru import logger

from app.core.exceptions import NotFoundException, ForbiddenException, \
    BadRequestException
from app.models.course import CourseORM
from app.repositories.lesson import LessonRepository


class LessonService:
    def __init__(self, lesson_repo: LessonRepository):
        self.lesson_repo = lesson_repo