from fastapi import HTTPException
from starlette import status

from app.models.user import UserORM
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token

from loguru import logger

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, user: UserCreate):
        logger.info(f'Registration attempt for email: {user.email}')

        existing_user = await self.repository.get_by_email(user.email)
        if existing_user:
            logger.warning(f'User {user.email} already exists')
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
        try:
            created_user = await self.repository.create(db_user)
            logger.success(f'Created a new user: {user.email} with ID: {created_user.id}')
        except Exception:
            logger.exception(f'Failed to create new user: {user.email}')
            raise
        return UserResponse.model_validate(created_user)

    async def login(self, user_name: str, password: str) -> dict:
        logger.info(f'Login attempt for user_name: {user_name}')
        user = await self.repository.get_by_username(user_name)
        if user is None:
            logger.warning(f'Login failed: User {user_name} not found')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password"
            )

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed: Incorrect password for user {user_name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password"
            )
        try:
            access_token = create_access_token(
                data={"sub": user.email, "username": user.username, "id": user.id},
            )
            logger.success(f'Access token created for {user_name} with ID: {user.id}')
        except Exception:
            logger.exception(f"Unexpected error during token generation for {user_name}")
            raise
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_profile(self, current_user: UserORM) -> UserResponse:
        return UserResponse.model_validate(current_user)