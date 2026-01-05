from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import CourseORM
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CourseORM)

    async def get_my_courses(self, user_id: int) -> Sequence[CourseORM]:
        result = await self.session.scalars(
            select(CourseORM).where(CourseORM.author_id == user_id)
        )
        return result.all()