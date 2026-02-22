from datetime import datetime

from app.repositories.lesson_completion import LessonCompletionRepository
from app.services.purchase import PurchaseService
from app.repositories.progress import ProgressRepository


class LessonCompletionService:
    def __init__(self,progress_repo: ProgressRepository, lesson_completion_repo: LessonCompletionRepository, purchase_service: PurchaseService):
        self.lesson_completion_repo = lesson_completion_repo
        self.purchase_service = purchase_service
        self.progress_repo = progress_repo

    async def mark_lesson_as_complete(self, user_id: int, lesson_id: int, course_id: int):
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
        await self.lesson_completion_repo.delete_completion(user_id, lesson_id)
        return await self.lesson_completion_repo.update_course_progress(user_id, course_id, lesson_id)

    async def get_progress_for_course(self, user_id: int, course_id: int):
        main_progress = await self.progress_repo.get_progress_for_course(user_id=user_id, course_id=course_id)

        completed_ids = await self.lesson_completion_repo.get_completed_lesson_ids(user_id=user_id, course_id=course_id)

        if not main_progress:
            return {
                "course_id": course_id,
                "current_lesson_id": 0,
                "is_completed": False,
                "completed_lessons": [],
                "last_accessed": datetime.now(),
                "progress_percentage": 0.0
            }
        return {
            "course_id": main_progress.course_id,
            "current_lesson_id": main_progress.current_lesson_id or 0,
            "completed_lessons": completed_ids,
            "is_completed": main_progress.is_completed,
            "last_accessed": main_progress.last_accessed,
            "progress_percentage": float(main_progress.progress_percentage)
        }

    async def get_my_progress_for_all_courses(self, user_id: int):
        return await self.progress_repo.get_all_progress_for_courses(user_id=user_id)
