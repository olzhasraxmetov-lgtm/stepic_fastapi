from app.repositories.comment import CommentRepository
from app.services.step import StepService
from app.models.user import UserORM
from app.models.comment import CommentORM
from app.core.exceptions import NotFoundException
from app.schemas.comment import CommentResponse, CommentAuthor


class CommentService:
    def __init__(self, comment_repo: CommentRepository, step_service: StepService):
        self.comment_repo = comment_repo
        self.step_service = step_service

    async def get_tree_of_comments(self, step_id: int, user: UserORM):
        step = await self.step_service.get_step_with_details(step_id)
        if not step:
            raise NotFoundException('Step not found')
        await self.step_service._check_access(
            user=user,
            lesson=step.lesson,
            error_message='Просматривать комментарии могут только участники курса. Пожалуйста, приобретите его.'
        )
        all_comments = await self.comment_repo.get_comments_for_step(step_id)
        roots = {}
        replies = []
        for comment in all_comments:
            comment_dto = CommentResponse(
                id=comment.id,
                content=comment.content,
                parent_id=comment.parent_id,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                author=CommentAuthor.model_validate(comment.author),
                children=[]
            )

            if comment_dto.parent_id is None:
                roots[comment_dto.id] = comment_dto
            else:
                replies.append(comment_dto)

        for reply in replies:
            if reply.parent_id in roots:
                roots[reply.parent_id].children.append(reply)

        return list(roots.values())

    async def leave_comment(self, step_id: int, user: UserORM, content: str):
        step = await self.step_service.get_step_with_details(step_id)
        if not step:
            raise NotFoundException('Step not found')
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
