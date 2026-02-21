from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exists
from app.models.progress import UserLessonCompletionORM
from app.repositories.base import BaseRepository
from app.models.lesson import LessonORM


class LessonCompletionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserLessonCompletionORM)

    async def check_lesson_belongs_to_course(self, lesson_id: int, course_id: int) -> bool:
        query = (
            select(exists().where(
                LessonORM.id == lesson_id,
                LessonORM.course_id == course_id
            ))
        )
        result = await self.session.execute(query)
        return result.scalar() or False
