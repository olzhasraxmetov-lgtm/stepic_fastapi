from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserORM
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserORM)

    async def get_by_username(self, username: str) -> UserORM | None:
        result = await self.session.scalars(
            select(UserORM).where(UserORM.username == username)
        )
        return result.first()

    async def get_by_email(self, email: EmailStr) -> UserORM | None:
        result = await self.session.scalars(
            select(UserORM).where(UserORM.email == email)
        )
        return result.first()