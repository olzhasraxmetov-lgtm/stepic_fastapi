from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.user import UserORM

from sqlalchemy import select

class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserORM)

    async def get_by_username(self, username: str) -> UserORM | None:
        result = await self.session.scalars(
            select(UserORM).where(UserORM.username == username)
        )
        return result.first()