from app.core.exceptions import BadRequestException, ForbiddenException
from app.models.user import UserORM
from app.repositories.reaction import ReactionRepository
from app.services.comment import CommentService
from app.services.notification import NotificationService
from loguru import logger

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
            logger.warning(
                f"Reaction denied: user_id={user.id} attempted to react to own comment_id={comment_id}"
            )
            raise BadRequestException(message='Вы не можете поставить лайк на свой комментарий')

        reaction = await self.reaction_repository.toggle_reaction(comment_id, user.id, is_like)
        await self.reaction_repository.session.commit()
        logger.info(
            f"Reaction applied: action={reaction}, user_id={user.id}, comment_id={comment.id}, is_like={is_like}"
        )

        if reaction == 'created' and is_like and comment.user_id != user.id:
            try:
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
                logger.info(
                    f"Like notification sent successfully: to_user_id={comment.user_id}, from_user_id={user.id}, comment_id={comment.id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to send like notification: to_user_id={comment.user_id}, from_user_id={user.id}, "
                    f"comment_id={comment.id}, error={str(e)}"
                )


        return {"status": "success", "action": reaction}