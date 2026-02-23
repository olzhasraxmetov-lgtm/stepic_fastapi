from loguru import logger

from app.core.exceptions import NotFoundException, ForbiddenException, \
    BadRequestException
from app.helpers.user_role import UserRoleEnum
from app.models.course import CourseORM
from app.models.user import UserORM
from app.repositories.course import CourseRepository
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate


class CourseService:

    def __init__(self, course_repo: CourseRepository):
        self.course_repo = course_repo

    async def get_paginated_courses(
            self,
            page: int,
            per_page: int,
            min_price: float | None,
            max_price: float | None,
    ):
        if min_price is not None and max_price is not None and min_price > max_price:
            raise BadRequestException(
                message='Минимальная цена не может быть больше максимальной цены'
            )

        return await self.course_repo.get_paginated_courses_with_filters(
            page=page,
            per_page=per_page,
            min_price=min_price,
            max_price=max_price,
        )

    async def _get_course_or_404(self, course_id: int) -> CourseORM:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundException(message='Курс не найден')
        return course

    def _check_course_access(self, course: CourseORM, user: UserORM) -> None:
        if not (user.is_admin or course.author_id == user.id):
            logger.warning(
                f"Access denied for user_id={user.id} to course_id={course.id}"
            )
            raise ForbiddenException(message="У вас недостаточно прав")

    async def get_by_id(self, course_id: int) -> CourseORM:
        return await self._get_course_or_404(course_id)

    async def create_course(self, current_user: UserORM, payload: CourseCreate) -> CourseResponse:
        logger.debug(
            f"CourseService.create_course started for user_id={current_user.id}"
        )
        if current_user.role not in [UserRoleEnum.AUTHOR, UserRoleEnum.ADMIN]:
            logger.warning(
                f"Course creation forbidden for user_id={current_user.id} with role={current_user.role}"
            )
            raise ForbiddenException(
                message='Только авторы могут создавать курс',
                log_message=f'Пользователь {current_user.id} с ролью {current_user.role} попытался создать курс'
            )
        created_course = payload.model_dump()
        created_course['author_id'] = current_user.id

        try:
            created_course = await self.course_repo.create(created_course)
            logger.success(
                f"Course successfully created: title='{payload.title}', author_id={current_user.id}, course_id={created_course.id}"
            )
            return CourseResponse.model_validate(created_course)
        except Exception as e:
            logger.exception(
                f"Database error while creating course title='{payload.title}' by user_id={current_user.id}: {e}"
            )
        raise


    async def get_my_courses(self, user_id: int) -> list[CourseResponse]:
        courses = await self.course_repo.get_my_courses(user_id)
        return [CourseResponse.model_validate(course) for course in courses]

    async def update_course(self, current_user: UserORM, course_id: int, payload: CourseUpdate) -> CourseResponse:
        db_course = await self._get_course_or_404(course_id)

        self._check_course_access(db_course, current_user)

        updated_data = payload.model_dump(exclude_unset=True)

        updated_course = await self.course_repo.update(course_id, updated_data)
        logger.success(
            f"Course updated successfully: course_id={course_id}, updated_by_user_id={current_user.id}"
        )
        return CourseResponse.model_validate(updated_course)

    async def delete_course(self, current_user: UserORM, course_id: int) -> dict:
        db_course = await self._get_course_or_404(course_id)

        self._check_course_access(db_course, current_user)

        await self.course_repo.delete_course(course_id)
        logger.success(
            f"Course deleted successfully: course_id={course_id}, deleted_by_user_id={current_user.id}"
        )
        return {"message": "Курс успешно удален"}


    async def publish_course(self, current_user: UserORM, course_id: int):
        db_course = await self._get_course_or_404(course_id)

        self._check_course_access(db_course, current_user)

        new_status = not db_course.is_published
        await self.course_repo.update(course_id, {'is_published': new_status})
        logger.success(
            f"Course publish status changed: course_id={course_id}, is_published={new_status}, changed_by_user_id={current_user.id}"
        )
        return {"id": course_id, "is_published": new_status}