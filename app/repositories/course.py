from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.course import CourseORM


class CourseRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CourseORM)
        