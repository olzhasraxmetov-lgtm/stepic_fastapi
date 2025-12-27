from fastapi import HTTPException
from starlette import status

from app.models.user import UserORM
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, user: UserCreate):
        existing_user = await self.repository.get_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {user.email} already exists"
            )

        db_user = UserORM(
            email=str(user.email),
            username=user.username,
            full_name=user.full_name,
            hashed_password=hash_password(user.password),
        )
        created_user = await self.repository.create(db_user)
        return UserResponse.model_validate(created_user)

    async def login(self, user_name: str, password: str) -> dict:
        user = await self.repository.get_by_username(user_name)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password"
            )

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password"
            )
        access_token = create_access_token(
            data={"sub": user.email, "username": user.username, "id": user.id},
        )
        return {"access_token": access_token, "token_type": "bearer"}