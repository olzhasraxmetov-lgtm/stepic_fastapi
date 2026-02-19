from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import UserCourseProgressORM
from app.repositories.base import BaseRepository


class ProgressRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserCourseProgressORM)