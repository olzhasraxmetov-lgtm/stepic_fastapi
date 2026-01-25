from typing import Sequence

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import LessonORM
from app.repositories.base import BaseRepository


class LessonRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LessonORM)

    async def get_all_lessons(self, course_id: int) -> Sequence[LessonORM]:
        result = await self.session.scalars(
            select(LessonORM).where(LessonORM.course_id == course_id)
        )
        return result.all()