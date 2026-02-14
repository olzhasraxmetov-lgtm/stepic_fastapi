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
from sqlalchemy import func, and_
from app.helpers.purchase_status import PurchaseStatus
from app.models.reaction import ReactionORM
from app.models.user import UserORM
from app.models.lesson import LessonORM


class CommentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CommentORM)

    async def create_comment(self, comment_obj: CommentORM) -> CommentORM:
        self.session.add(comment_obj)
        await self.session.commit()
        await self.session.refresh(comment_obj)
        return comment_obj

    def _get_comment_with_reactions_query(self, user_id: int | None = None):
        likes_sq = select(func.count(ReactionORM.comment_id)).where(
            and_(
                ReactionORM.comment_id == CommentORM.id,
                ReactionORM.is_like == True
            )
        ).scalar_subquery()

        dislikes_sq = select(func.count(ReactionORM.comment_id)).where(
            and_(
                ReactionORM.comment_id == CommentORM.id,
                ReactionORM.is_like == False
            )
        ).scalar_subquery()

        columns = [
            CommentORM,
            likes_sq.label("likes_count"),
            dislikes_sq.label("dislikes_count")
        ]

        if user_id:
            is_l = exists().where(
                and_(
                    ReactionORM.comment_id == CommentORM.id,
                    ReactionORM.user_id == user_id,
                    ReactionORM.is_like == True
                )
            ).label("is_liked_by_me")

            is_d = exists().where(
                and_(
                    ReactionORM.comment_id == CommentORM.id,
                    ReactionORM.user_id == user_id,
                    ReactionORM.is_like == False
                )
            ).label("is_disliked_by_me")

            columns.extend([is_l, is_d])

        return select(*columns)

    async def get_comments_for_step(self, step_id: int, user_id: int):
        query = self._get_comment_with_reactions_query(user_id)
        query = query.where(CommentORM.step_id == step_id).options(
            joinedload(CommentORM.author),
            joinedload(CommentORM.step)
        )
        comments = await self.session.execute(query)
        return comments.all()

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

    async def get_all_course_comments(self, course_id: int, user_id: int):
        query = self._get_comment_with_reactions_query(user_id)

        query = (
            query.join(StepORM, CommentORM.step_id == StepORM.id)
            .join(LessonORM, StepORM.lesson_id == LessonORM.id)
            .where(
                LessonORM.course_id == course_id,
                CommentORM.is_deleted == False
            )
            .options(
                joinedload(CommentORM.author),
                joinedload(CommentORM.step)
            )
            .order_by(CommentORM.created_at.desc())
        )

        result = await self.session.execute(query)
        return result.all()