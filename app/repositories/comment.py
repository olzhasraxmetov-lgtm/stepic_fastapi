from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ForbiddenException, \
    BadRequestException
from app.repositories.base import BaseRepository
from app.models.comment import CommentORM


class CommentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CommentORM)

    async def create_comment(self, comment_obj: CommentORM) -> CommentORM:
        self.session.add(comment_obj)
        await self.session.commit()
        await self.session.refresh(comment_obj)
        return comment_obj