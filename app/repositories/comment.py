from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import NotFoundException, ForbiddenException, \
    BadRequestException
from app.repositories.base import BaseRepository
from app.models.comment import CommentORM
from sqlalchemy import select, update, exists

from app.models.step import StepORM
from app.models.course import CourseORM
from app.models.purchace import PurchaseORM
from app.helpers.purchase_status import PurchaseStatus


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
                joinedload(CommentORM.author),
                joinedload(CommentORM.step)
            )
        )
        comments = await self.session.execute(query)
        return comments.scalars().all()

    async def update_comment_with_author(self, comment_id: int, data: dict):
        updated_comment = await self.update(comment_id, data)

        if updated_comment:
            await self.session.refresh(updated_comment, attribute_names=['author'])
        return updated_comment

    async def check_user_enrollment(self, user_id: int, course_id: int) -> bool:
        query = (
            select(exists().where(
                PurchaseORM.user_id == user_id,
                PurchaseORM.course_id == course_id,
                PurchaseORM.status == PurchaseStatus.SUCCEEDED
            ))
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_all_comments_for_course(self, course_id: int):
        query = (
            select(CommentORM).where(CommentORM.course_id == course_id,
                                     CommentORM.is_deleted == False)
            .options(
                joinedload(CommentORM.author),
                joinedload(CommentORM.step)
            )
            .order_by(CommentORM.created_at.desc())
        )
        comments = await self.session.execute(query)
        return comments.scalars().all()