from app.core.exceptions import BadRequestException
from app.models.user import UserORM
from app.repositories.reaction import ReactionRepository
from app.services.comment import CommentService
from app.services.notification import NotificationService


class ReactionService:
    def __init__(self, reaction_repository: ReactionRepository, comment_service: CommentService, notification_service: NotificationService):
        self.reaction_repository = reaction_repository
        self.comment_service = comment_service
        self.notification_service = notification_service

    async def toggle_reaction(self, comment_id: int, user: UserORM, is_like: bool):
        comment, _ = await self.comment_service.get_comment_and_check_rights(
            comment_id, user, check_author=False
        )

        if comment.user_id == user.id:
            raise BadRequestException(message='Вы не можете лайкать свой комментарий')

        reaction = await self.reaction_repository.toggle_reaction(comment_id, user.id, is_like)
        await self.reaction_repository.session.commit()


        if reaction == 'created' and is_like and comment.user_id != user.id:
            notification_data = {
                'type': 'new_like',
                "from_user": user.username,
                "comment_id": comment.id,
                "is_read": False,
                "comment_text": comment.content[:50] + '...' if len(comment.content) > 50 else comment.content,
            }

            await self.notification_service.send_notification(
                target_user_id=comment.user_id,
                payload=notification_data
            )


        return {"status": "success", "action": reaction}