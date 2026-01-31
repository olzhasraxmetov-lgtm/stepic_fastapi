from loguru import logger

from app.core.exceptions import NotFoundException
from app.models.course import CourseORM
from app.models.lesson import LessonORM
from app.repositories.lesson import LessonRepository
from app.repositories.purchase import PurchaseRepository
from app.schemas.lesson import LessonCreate, LessonUpdate


class LessonService:
    def __init__(self, lesson_repo: LessonRepository, purchase_repo: PurchaseRepository):
        self.lesson_repo = lesson_repo
        self.purchase_repo = purchase_repo


    async def get_lesson_or_404(self, lesson_id: int) -> LessonORM:
        lesson_db: LessonORM = await self.lesson_repo.get_with_steps(lesson_id, use_selection=True)
        if not lesson_db:
            raise NotFoundException(message=f'Lesson not found')
        return lesson_db

    async def create_lesson(self, course: CourseORM, payload: LessonCreate):
        lesson_data = payload.model_dump()
        lesson_data['course_id'] = course.id

        return await self.lesson_repo.create(lesson_data)

    async def update_lesson(self, lesson: LessonORM, payload: LessonUpdate):
        data = payload.model_dump(exclude_unset=True)

        updated_data = await self.lesson_repo.update(object_id=lesson.id, data=data)
        await self.lesson_repo.session.refresh(updated_data, attribute_names=['steps'])

        return updated_data


    async def delete_lesson(self, lesson: LessonORM) -> dict:
        await self.lesson_repo.delete(lesson.id)
        logger.success(f'Successfully deleted {lesson.id}')
        return {"message": "Lesson deleted successfully"}

    async def get_all_lessons(self, course_id: int):
        return await self.lesson_repo.get_all_lessons(course_id)