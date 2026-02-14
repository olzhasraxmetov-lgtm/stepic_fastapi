from app.repositories.comment import CommentRepository
from app.services.step import StepService
from app.models.user import UserORM
from app.models.comment import CommentORM
from app.core.exceptions import NotFoundException, ForbiddenException
from app.schemas.comment import CommentFullResponse, CommentAuthor, CommentUpdate
from app.helpers.user_role import UserRoleEnum

class CommentService:
    def __init__(self, comment_repo: CommentRepository, step_service: StepService):
        self.comment_repo = comment_repo
        self.step_service = step_service

    async def get_step_and_check_access(self, step_id: int, user: UserORM, error_msg: str):
        step = await self.step_service.get_step_with_details(step_id)
        if not step:
            raise NotFoundException('Шаг не найден')
        await self.step_service._check_access(
            user=user,
            lesson=step.lesson,
            error_message=error_msg
        )
        return step

    async def get_comment_and_check_rights(self, comment_id: int, user: UserORM, check_author: bool = True):
        existing_comment: CommentORM = await self.comment_repo.get_by_id(comment_id)
        if not existing_comment:
            raise NotFoundException(message='Комментарий не найден')

        step = await self.get_step_and_check_access(
            existing_comment.step_id, user, "У вас нет доступа к курсу."
        )

        if check_author:
            is_author = existing_comment.user_id == user.id
            is_admin = user.role == UserRoleEnum.ADMIN
            if not (is_author or is_admin):
                raise ForbiddenException('Недостаточно прав для действий')

        return existing_comment, step

    def _build_comment_response(
            self,
            comment: CommentORM,
            author_obj=None,
            likes: int = 0, dislikes: int = 0,
            is_liked: bool = False,
            is_disliked: bool = False,
    ) -> CommentFullResponse:
        author = author_obj or comment.author
        return CommentFullResponse(
            id=comment.id,
            content=comment.content,
            step_title=comment.step.title if comment.step else None,
            parent_id=comment.parent_id,
            likes_count=likes,
            dislikes_count=dislikes,
            created_at=comment.created_at,
            is_deleted=comment.is_deleted,
            is_disliked_by_me=is_disliked,
            is_edited=comment.is_edited,
            updated_at=comment.updated_at,
            is_liked_by_me=is_liked,
            author=CommentAuthor.model_validate(author),
            children=[]
        )

    async def get_tree_of_comments(self, step_id: int, user: UserORM):
        step = await self.get_step_and_check_access(step_id, user, 'Оставлять комментарии могут только участники курса.')

        all_comments = await self.comment_repo.get_comments_for_step(step_id, user.id)
        roots = {}
        replies = []
        for comment, likes, dislike, is_liked, is_disliked in all_comments:
            comment_dto = self._build_comment_response(comment, likes=likes, dislikes=dislike, is_liked=is_liked, is_disliked=is_disliked)
            comment_dto.step_title = step.title

            if comment_dto.parent_id is None:
                roots[comment_dto.id] = comment_dto
            else:
                replies.append(comment_dto)

        for reply in replies:
            if reply.parent_id in roots:
                roots[reply.parent_id].children.append(reply)

        return list(roots.values())

    async def leave_comment(self, step_id: int, user: UserORM, content: str):
        step = await self.get_step_and_check_access(step_id, user, 'Оставлять комментарии могут только участники курса.')

        new_comment = CommentORM(
            step_id=step_id,
            user_id=user.id,
            course_id=step.lesson.course_id,
            content=content,
            parent_id=None
        )

        return await self.comment_repo.create_comment(new_comment)

    async def reply_to_comment(self, comment_id: int, user: UserORM, content: str):
        existing_comment, step = await self.get_comment_and_check_rights(comment_id, user)

        effective_parent_id = existing_comment.parent_id or existing_comment.id

        new_comment = CommentORM(
            step_id=existing_comment.step_id,
            user_id=user.id,
            course_id=step.lesson.course_id,
            content=content,
            parent_id=effective_parent_id
        )
        created = await self.comment_repo.create_comment(new_comment)
        return self._build_comment_response(created)

    async def soft_delete_comment(self, comment_id: int, user: UserORM):
        comment, _ = await self.get_comment_and_check_rights(comment_id, user)

        updated = await self.comment_repo.update(comment_id, data={
            "content": 'Сообщение удалено пользователем',
            'is_deleted': True
        })
        return self._build_comment_response(updated, author_obj=comment.author)

    async def update_comment(self, comment_id: int, user: UserORM, payload: CommentUpdate):
        comment, _ = await self.get_comment_and_check_rights(comment_id, user)

        update_data = payload.model_dump(exclude_unset=True)
        update_data["is_edited"] = True

        updated = await self.comment_repo.update(comment_id, data=update_data)
        return self._build_comment_response(updated, author_obj=comment.author)

    async def get_all_course_comments(self, course_id: int, user: UserORM):
        if user.role != UserRoleEnum.ADMIN:
            is_enrolled = await self.comment_repo.check_user_enrollment(user.id, course_id)
            if not is_enrolled:
                raise ForbiddenException('Доступ к обсуждениям закрыт. Купите курс.')

        comments = await self.comment_repo.get_all_course_comments(course_id, user.id)

        return [
            self._build_comment_response(
                comment=row[0],
                likes=row[1],
                dislikes=row[2]
            )
            for row in comments
        ]