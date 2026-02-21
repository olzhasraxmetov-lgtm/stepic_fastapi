from app.repositories.progress import LessonCompletionRepository
from app.services.purchase import PurchaseService
from app.core.exceptions import ForbiddenException,NotFoundException

class LessonCompletionService:
    def __init__(self, lesson_completion_repo: LessonCompletionRepository, purchase_service: PurchaseService):
        self.lesson_completion_repo = lesson_completion_repo
        self.purchase_service = purchase_service

    async def _check_access_and_belongs(self,user_id: int, lesson_id: int, course_id: int):
        is_course_paid = await self.purchase_service.check_is_course_paid(user_id, course_id)
        if not is_course_paid:
            raise ForbiddenException(message='Вы не купили курс!')

        lesson = await self.lesson_completion_repo.check_lesson_belongs_to_course(lesson_id, course_id)
        if not lesson:
            raise NotFoundException(message='Урок не найден в данном курсе')

    async def mark_lesson_as_complete(self, user_id: int, lesson_id: int, course_id: int):
        await self._check_access_and_belongs(user_id, lesson_id, course_id)
        is_already_completed = await self.lesson_completion_repo.check_exists(user_id, lesson_id)

        if not is_already_completed:
            completion_data = {
                "user_id": user_id,
                "lesson_id": lesson_id,
                "course_id": course_id,
            }
            await self.lesson_completion_repo.create(data=completion_data)  # type: ignore

        new_progress = await self.lesson_completion_repo.update_course_progress(user_id, course_id, lesson_id)

        return {
            "status": "success",
            "new_percentage": new_progress,
            "is_completed": new_progress >= 100,
            "lesson_id": lesson_id
        }

    async def unmark_lesson_as_complete(self, user_id: int, lesson_id: int, course_id: int):
        await self._check_access_and_belongs(user_id, lesson_id, course_id)
        await self.lesson_completion_repo.delete_completion(user_id, lesson_id)
        return await self.lesson_completion_repo.update_course_progress(user_id, course_id, lesson_id)


