from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.reaction import ReactionORM
from app.models.user import UserORM
from sqlalchemy import select


class ReactionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ReactionORM)

    async def toggle_reaction(self, comment_id: int, user_id: int, is_like: bool):
        query = (
            select(ReactionORM)
            .where(ReactionORM.comment_id == comment_id)
            .where(ReactionORM.user_id == user_id)
        )
        result = await self.session.execute(query)
        reaction = result.scalar_one_or_none()

        if reaction is None:
            new_reaction = ReactionORM(
                comment_id=comment_id,
                user_id=user_id,
                is_like=is_like,
            )
            self.session.add(new_reaction)
            return 'created'
        if reaction.is_like == is_like:
            await self.session.delete(reaction)
            return "deleted"

        reaction.is_like = is_like
        return 'updated'

