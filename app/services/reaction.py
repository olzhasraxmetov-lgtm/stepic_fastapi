from app.repositories.reaction import ReactionRepository


class ReactionService:
    def __init__(self, repository: ReactionRepository):
        self.repository = repository