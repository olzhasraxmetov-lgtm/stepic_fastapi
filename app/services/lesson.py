from loguru import logger

from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.course import CourseORM
from app.models.lesson import LessonORM
from app.models.user import UserORM
from app.repositories.lesson import LessonRepository
from app.schemas.lesson import LessonCreate, LessonUpdate


class LessonService:
    def __init__(self, lesson_repo: LessonRepository):
        self.lesson_repo = lesson_repo


    async def get_lesson_or_404(self, lesson_id: int) -> LessonORM:
        lesson_db: LessonORM = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson_db:
            raise NotFoundException(message=f'Lesson not found')
        return lesson_db

    async def create_lesson(self, course: CourseORM, current_user: UserORM, payload: LessonCreate):
        if course.author_id != current_user.id:
            raise ForbiddenException(
                message='You are not authorized to access this lesson',
                log_message=f'User with {course.author_id} tried to access the course with {course.id}'
            )


        lesson_data = payload.model_dump()
        lesson_data['course_id'] = course.id

        return await self.lesson_repo.create(lesson_data)

    async def check_lesson_belongs_to_course(self, course: CourseORM, lesson: LessonORM) -> bool:
        if not lesson or lesson.course_id != course.id:
            raise NotFoundException(message=f'Lesson {lesson.id} not found in the course {course.id}')
        return True

    async def update_lesson(self, lesson_id: int ,course: CourseORM, payload: LessonUpdate):
        lesson_db: LessonORM = await self.get_lesson_or_404(lesson_id)
        await self.check_lesson_belongs_to_course(course, lesson_db)

        data = payload.model_dump(exclude_unset=True)

        return await self.lesson_repo.update(object_id=lesson_id, data=data)

    async def delete_lesson(self, lesson_id: int, course: CourseORM) -> dict:
        lesson_db: LessonORM = await self.get_lesson_or_404(lesson_id)
        await self.check_lesson_belongs_to_course(course, lesson_db)

        await self.lesson_repo.delete(lesson_id)
        logger.success(f'Successfully deleted {lesson_id} by user: {course.author_id}')
        return {"message": "Lesson deleted successfully"}

    async def get_all_lessons(self, course_id: int):
        return await self.lesson_repo.get_all_lessons(course_id)