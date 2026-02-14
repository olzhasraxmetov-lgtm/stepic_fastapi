from app.repositories.reaction import ReactionRepository
from app.services.comment import CommentService

class ReactionService:
    def __init__(self, reaction_repository: ReactionRepository, comment_service: CommentService):
        self.reaction_repository = reaction_repository
        self.comment_service = comment_service