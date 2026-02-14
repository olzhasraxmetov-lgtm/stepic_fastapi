from app.repositories.reaction import ReactionRepository
from app.services.comment import CommentService
from app.models.user import UserORM


class ReactionService:
    def __init__(self, reaction_repository: ReactionRepository, comment_service: CommentService):
        self.reaction_repository = reaction_repository
        self.comment_service = comment_service

    async def toggle_reaction(self, comment_id: int, user: UserORM, is_like: bool):
        await self.comment_service.get_comment_and_check_rights(comment_id, user, check_author=False)
        reaction = await self.reaction_repository.toggle_reaction(comment_id, user.id, is_like)
        await self.reaction_repository.session.commit()
        return {"status": "success", "action": reaction}