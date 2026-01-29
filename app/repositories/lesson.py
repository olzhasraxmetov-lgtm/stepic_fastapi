from typing import Sequence

from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import LessonORM
from app.repositories.base import BaseRepository
from app.models.course import CourseORM


class LessonRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LessonORM)

    async def get_with_steps(self, lesson_id: int, use_selection: bool) -> LessonORM:
        query = select(LessonORM).where(LessonORM.id == lesson_id)
        if use_selection:
            query = query.options(selectinload(LessonORM.steps))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_lessons(self, course_id: int) -> Sequence[LessonORM]:
        result = await self.session.scalars(
            select(LessonORM).where(LessonORM.course_id == course_id)
            .options(selectinload(LessonORM.steps))
            .order_by(LessonORM.order_number)
        )
        return result.all()