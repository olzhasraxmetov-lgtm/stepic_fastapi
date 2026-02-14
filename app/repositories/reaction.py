from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.reaction import ReactionORM

class ReactionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ReactionORM)

