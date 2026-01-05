from loguru import logger
from typing import Sequence

from sqlalchemy.sql.functions import current_user

from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException, ForbiddenException, \
    BaseAppException
from app.helpers.user_role import UserRoleEnum
from app.models.course import CourseORM
from app.models.user import UserORM
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.repositories.course import CourseRepository

class CourseService:

    def __init__(self, course_repo: CourseRepository):
        self.course_repo = course_repo

    async def create_course(self, current_user: UserORM, payload: CourseCreate) -> CourseResponse:
        logger.debug(f'Attempting to create a course by user: {current_user.id}')
        if current_user.role not in [UserRoleEnum.AUTHOR, UserRoleEnum.ADMIN]:
            logger.warning(f'Failed to create a course by user:  {current_user.id}')
            raise ForbiddenException(
                message='Only authors can create courses',
                log_message=f'User {current_user.id} with role {current_user.role} tried to create course'
            )
        created_course = payload.model_dump()
        created_course['author_id'] = current_user.id

        try:
            created_course = await self.course_repo.create(created_course)
            logger.success(f'Successfully created {payload.title} by user: {current_user.id}')
            return CourseResponse.model_validate(created_course)
        except Exception as e:
            logger.exception(f"Database error while creating course '{payload.title}': {e}")
        raise

    async def get_course_by_id(self, course_id: int) -> CourseResponse:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundException(
                message=f'Course with id {course_id} not found',
            )
        return CourseResponse.model_validate(course)

    async def get_my_courses(self, user_id: int) -> list[CourseResponse]:
        courses = await self.course_repo.get_my_courses(user_id)
        return [CourseResponse.model_validate(course) for course in courses]

    async def update_course(self, current_user: UserORM, course_id: int, payload: CourseUpdate) -> CourseResponse:
        db_course = await self.course_repo.get_by_id(course_id)

        if not db_course:
            raise NotFoundException(
                message=f'Course with id {course_id} not found',
            )

        is_author = db_course.author_id == current_user.id
        is_admin = current_user.role == UserRoleEnum.ADMIN

        if not (is_author or is_admin):
            logger.warning(f"Unauthorized update attempt by {current_user.email}")
            raise ForbiddenException(message="You don't have permission to edit this course")

        updated_data = payload.model_dump(exclude_unset=True)

        updated_course = await self.course_repo.update(course_id, updated_data)
        logger.success(f'Successfully updated {course_id} by user: {current_user.id}')
        return CourseResponse.model_validate(updated_course)

    async def delete_course(self, current_user: UserORM, course_id: int) -> dict:
        db_course = await self.course_repo.get_by_id(course_id)

        if not db_course:
            raise NotFoundException(
                message=f'Course with id {course_id} not found',
            )

        is_author = db_course.author_id == current_user.id
        is_admin = current_user.role == UserRoleEnum.ADMIN

        if not (is_author or is_admin):
            logger.warning(f"Unauthorized delete attempt by {current_user.email}")
            raise ForbiddenException(message="You don't have permission to delete this course")

        await self.course_repo.delete_course(course_id)
        logger.success(f'Successfully deleted {course_id} by user: {current_user.id}')
        return {"message": "Course deleted successfully"}