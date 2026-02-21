from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exists
from app.models.progress import UserLessonCompletionORM, UserCourseProgressORM
from app.repositories.base import BaseRepository
from app.models.lesson import LessonORM


class LessonCompletionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserLessonCompletionORM)

    async def update_course_progress(self, user_id: int, course_id: int, lesson_id: int):
        total_lessons_query = select(func.count()).select_from(LessonORM).where(LessonORM.course_id == course_id)
        total_result_count = await self.session.execute(total_lessons_query)
        total_count = total_result_count.scalar() or 0
        if total_count == 0:
            return 0

        completed_lessons_query = (
            select(func.count()).select_from(UserLessonCompletionORM)
            .where(UserLessonCompletionORM.user_id == user_id)
            .where(UserLessonCompletionORM.course_id == course_id)
        )

        completed_result = await self.session.execute(completed_lessons_query)
        completed_count = completed_result.scalar() or 0

        percentage = round(Decimal(completed_count) / Decimal(total_count) * 100, 2) if total_count > 0 else 0

        existing_course_progres_query = (
            select(UserCourseProgressORM)
            .where(UserCourseProgressORM.user_id == user_id)
            .where(UserCourseProgressORM.course_id == course_id)
        )
        result_progress = await self.session.execute(existing_course_progres_query)
        progress_record = result_progress.scalar_one_or_none()
        if progress_record:
            progress_record.progress_percentage = percentage
            progress_record.is_completed = (percentage >= 100)
            progress_record.current_lesson_id = lesson_id
        else:
            new_progress = UserCourseProgressORM(
                user_id=user_id,
                course_id=course_id,
                progress_percentage=percentage,
                current_lesson_id=lesson_id,
                is_completed=(percentage >= 100),
            )
            self.session.add(new_progress)
        await self.session.commit()
        return percentage



    async def check_lesson_belongs_to_course(self, lesson_id: int, course_id: int) -> bool:
        query = (
            select(exists().where(
                LessonORM.id == lesson_id,
                LessonORM.course_id == course_id
            ))
        )
        result = await self.session.execute(query)
        return result.scalar() or False

    async def delete_completion(self, user_id: int, lesson_id: int):
        query = (
            delete(UserLessonCompletionORM)
            .where(UserLessonCompletionORM.user_id == user_id)
            .where(UserLessonCompletionORM.lesson_id == lesson_id)
        )
        result = await self.session.execute(query)
        await self.session.commit()

    async def check_exists(self, user_id: int, lesson_id: int) -> bool:
        query = (
            select(exists().where(
                UserLessonCompletionORM.user_id == user_id,
                UserLessonCompletionORM.lesson_id == lesson_id
            ))
        )
        result = await self.session.execute(query)
        return result.scalar() or False