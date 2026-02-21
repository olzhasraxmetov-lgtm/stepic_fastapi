from app.repositories.lesson_completion import LessonCompletionRepository
from app.services.purchase import PurchaseService
from app.core.exceptions import ForbiddenException,NotFoundException

class LessonCompletionService:
    def __init__(self, lesson_completion_repo: LessonCompletionRepository, purchase_service: PurchaseService):
        self.lesson_completion_repo = lesson_completion_repo
        self.purchase_service = purchase_service


    async def mark_lesson_as_complete(self, user_id: int, lesson_id: int, course_id: int):
        is_course_paid = await self.purchase_service.check_is_course_paid(user_id, course_id)
        if not is_course_paid:
            raise ForbiddenException(message='Вы не купили курс!')

        lesson = await self.lesson_completion_repo.check_lesson_belongs_to_course(lesson_id, course_id)
        if not lesson:
            raise NotFoundException(message='Урок не найден в данном курсе')

        completion_data = {
            "user_id": user_id,
            "lesson_id": lesson_id,
            "course_id": course_id,
        }
        return await self.lesson_completion_repo.create(data=completion_data) #type: ignore
