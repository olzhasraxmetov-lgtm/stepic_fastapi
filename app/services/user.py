
from app.repositories.user import UserRepository

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self):
        pass