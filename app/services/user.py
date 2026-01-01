from fastapi import HTTPException
from starlette import status

from app.models.user import UserORM
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserPublic, UserUpdate
from app.utils.security import hash_password, verify_password, create_access_token
import os
from loguru import logger
from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException, ForbiddenException, BaseAppException
from app.helpers.user_role import UserRoleEnum
from app.schemas.user import AdminCreate
from app.core.config import config
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, user: UserCreate):
        logger.info(f'Registration attempt for email: {user.email}')

        existing_user = await self.repository.get_by_email(user.email)
        if existing_user:
            raise ConflictException(f'User with email {user.email} already exists')

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
            raise UnauthorizedException(
                message='Incorrect username or password',
                log_message=f'User {user_name} not found'
            )

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException(
                message="Incorrect username or password",
                log_message=f"Login failed: Wrong password for user {user_name}"
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

    async def get_public_profile_by_id(self, user_id: int) -> UserPublic:
        logger.debug(f'Attempting to fetch user profile by ID: {user_id}')
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(f'User with ID {user_id} not found')
        return UserPublic.model_validate(user)

    async def update_profile(self, current_user: UserORM, payload: UserUpdate) -> UserResponse:
        updated_data = payload.model_dump(exclude_unset=True)
        logger.debug(f'Updating user profile: {current_user.id}. Fields to change: {updated_data.keys()}')
        try:
            result = await self.repository.update_profile(obj=current_user, data=updated_data)
            logger.success(f'Updated user profile successfully: ID: {current_user.id}')
            return UserResponse.model_validate(result)
        except Exception as e:
            logger.exception(f'Failed to update user profile: {current_user.id}')
            raise BaseAppException(
                message=f'Failed to update user profile',
                log_message=f'Failed to update user profile: {current_user.id}: {str(e)}'

            )

    async def create_admin(self, payload: AdminCreate ) -> UserResponse:
        expected_key = config.ADMIN_SECRET_KEY

        if payload.admin_secret_key != expected_key:
            logger.warning(f'Failed to create admin user for email: {payload.email}')
            raise ForbiddenException(
                message=f'Invalid admin secret key',
                log_message=f'Failed to create admin user for email: {payload.email}'
            )

        existing_user = await self.repository.get_by_email(payload.email)
        if existing_user:
            raise ConflictException(
                f'User with email {payload.email} already exists'
            )

        hashed_password = hash_password(payload.password)

        new_admin_data = payload.model_dump(exclude={"admin_secret_key", "password"})
        new_admin_data['hashed_password'] = hashed_password
        new_admin_data['role'] = UserRoleEnum.ADMIN

        new_data = await self.repository.create(new_admin_data)
        logger.success(f'Created new admin user: {new_data.email} (ID: {new_data.id})')
        return UserResponse.model_validate(new_data)