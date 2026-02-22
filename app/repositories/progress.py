from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.progress import UserCourseProgressORM
from app.repositories.base import BaseRepository


class ProgressRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserCourseProgressORM)

    async def get_progress_for_course(self, user_id: int, course_id: int):
        query = (
            select(UserCourseProgressORM)
            .where(UserCourseProgressORM.user_id == user_id)
            .where(UserCourseProgressORM.course_id == course_id)
        )
        result = await self.session.execute(query)
        data = result.scalar_one_or_none()
        return data

    async def get_all_progress_for_courses(self, user_id: int):
        query = (
            select(UserCourseProgressORM)
            .options(
                joinedload(UserCourseProgressORM.course)
            )
            .where(UserCourseProgressORM.user_id == user_id)
            .order_by(UserCourseProgressORM.last_accessed.desc())
        )
        res = await self.session.execute(query)
        return res.scalars().all()
