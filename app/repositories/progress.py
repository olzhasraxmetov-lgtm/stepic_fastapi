from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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