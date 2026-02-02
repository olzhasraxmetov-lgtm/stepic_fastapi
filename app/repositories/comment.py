from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ForbiddenException, \
    BadRequestException
from app.repositories.base import BaseRepository
from app.models.comment import CommentORM


class CommentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CommentORM)