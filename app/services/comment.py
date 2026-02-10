from app.repositories.comment import CommentRepository
from app.services.step import StepService
from app.models.user import UserORM
from app.models.comment import CommentORM
from app.core.exceptions import NotFoundException


class CommentService:
    def __init__(self, comment_repo: CommentRepository, step_service: StepService):
        self.comment_repo = comment_repo
        self.step_service = step_service

    async def leave_comment(self, step_id: int, user: UserORM, content: str):
        step = await self.step_service.get_step_with_details(step_id)
        await self.step_service._check_access(
            user=user,
            lesson=step.lesson,
            error_message='Оставлять комментарии могут только участники курса. Пожалуйста, приобретите его.'
        )
        new_comment = CommentORM(
            step_id=step_id,
            user_id=user.id,
            course_id=step.lesson.course_id,
            content=content,
            parent_id=None
        )
        return await self.comment_repo.create_comment(new_comment)

    async def reply_to_comment(self, comment_id: int, user: UserORM, content: str):
        existing_comment: CommentORM = await self.comment_repo.get_by_id(comment_id)
        if not existing_comment:
            raise NotFoundException(message='Комментарий не найден')

        effective_parent_id = existing_comment.parent_id or existing_comment.id

        step = await self.step_service.get_step_with_details(existing_comment.step_id)


        await self.step_service._check_access(
            user=user,
            lesson=step.lesson,
            error_message='Оставлять комментарии могут только участники курса. Пожалуйста, приобретите его.'
        )

        new_comment = CommentORM(
            step_id=existing_comment.step_id,
            user_id=user.id,
            course_id=step.lesson.course_id,
            content=content,
            parent_id=effective_parent_id
        )
        return await self.comment_repo.create_comment(new_comment)
