from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import NotFoundException, ForbiddenException, \
    BadRequestException
from app.repositories.base import BaseRepository
from app.models.comment import CommentORM
from sqlalchemy import select

from app.models.step import StepORM


class CommentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CommentORM)

    async def create_comment(self, comment_obj: CommentORM) -> CommentORM:
        self.session.add(comment_obj)
        await self.session.commit()
        await self.session.refresh(comment_obj)
        return comment_obj

    async def get_comments_for_step(self, step_id: int):
        query = (
            select(CommentORM).where(CommentORM.step_id==step_id)
            .options(
                joinedload(CommentORM.author)
            )
        )
        comments = await self.session.execute(query)
        return comments.scalars().all()