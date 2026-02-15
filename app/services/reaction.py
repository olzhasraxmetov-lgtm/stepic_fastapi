from redis.asyncio.client import Redis
import json
from app.repositories.reaction import ReactionRepository
from app.services.comment import CommentService
from app.models.user import UserORM
from app.core.websocket_manager import manager
from app.core.exceptions import BadRequestException

class ReactionService:
    def __init__(self, reaction_repository: ReactionRepository, comment_service: CommentService, redis: Redis):
        self.reaction_repository = reaction_repository
        self.comment_service = comment_service
        self.redis = redis

    async def toggle_reaction(self, comment_id: int, user: UserORM, is_like: bool):
        comment, _ = await self.comment_service.get_comment_and_check_rights(
            comment_id, user, check_author=False
        )

        if comment.user_id == user.id:
            raise BadRequestException(message='Вы не можете лайкать свой комментарий')

        reaction = await self.reaction_repository.toggle_reaction(comment_id, user.id, is_like)
        await self.reaction_repository.session.commit()


        if reaction == 'created' and is_like and comment.user_id != user.id:
            notification = {
                'type': 'new_like',
                "from_user": user.username,
                "comment_id": comment.id,
                "comment_text": comment.content[:50] + '...' if len(comment.content) > 50 else comment.content,
            }

            redis_key = f'notifications:user:{comment.user_id}'
            await self.redis.lpush(redis_key, json.dumps(notification))
            await manager.send_personal_message(notification, comment.user_id)
            await self.redis.ltrim(redis_key, 0, 19)


        return {"status": "success", "action": reaction}