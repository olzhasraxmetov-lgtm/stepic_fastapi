from loguru import logger

from app.core.config import config
from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException, ForbiddenException, \
    BaseAppException
from app.helpers.user_role import UserRoleEnum
from app.models.user import UserORM
from app.repositories.user import UserRepository
from app.schemas.user import AdminCreate
from app.schemas.user import UserCreate, UserResponse, UserPublic, UserUpdate
from app.schemas.user import UserRoleUpdate
from app.utils.security import hash_password, verify_password, create_access_token


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, user: UserCreate):
        logger.info(f"User registration attempt: email='{user.email}'")

        existing_user = await self.repository.get_by_email(user.email)
        if existing_user:
            raise ConflictException(f'Пользователь с {user.email} уже существует!')

        user_data = user.model_dump()
        raw_password = user_data.pop('password')
        user_data["hashed_password"] = hash_password(raw_password)
        try:
            created_user = await self.repository.create(user_data)
            logger.success(
                f"User created successfully: email='{user.email}', user_id={created_user.id}"
            )
        except Exception:
            logger.exception(f"Failed to create new user: email='{user.email}'")
            raise
        return UserResponse.model_validate(created_user)

    async def login(self, user_name: str, password: str) -> dict:
        logger.info(f"User login attempt: username='{user_name}'")
        user = await self.repository.get_by_username(user_name)
        if user is None:
            raise UnauthorizedException(
                message='Неправильное имя пользователя или пароль',
                log_message=f'User {user_name} not found'
            )

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException(
                message="Неправильное имя пользователя или пароль",
                log_message=f"Login failed: Wrong password for user {user_name}"
            )
        try:
            access_token = create_access_token(
                data={"sub": user.email, "username": user.username, "id": user.id},
            )
            logger.success(
                f"Access token created: username='{user_name}', user_id={user.id}"
            )
        except Exception:
            logger.exception(
                f"Unexpected error during token generation for username='{user_name}'"
            )
            raise
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_profile(self, current_user: UserORM) -> UserResponse:
        return UserResponse.model_validate(current_user)

    async def get_public_profile_by_id(self, user_id: int) -> UserPublic:
        logger.debug(f"Fetching public user profile: user_id={user_id}")
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(f'Пользователь не найден')
        return UserPublic.model_validate(user)

    async def update_profile(self, current_user: UserORM, payload: UserUpdate) -> UserResponse:
        updated_data = payload.model_dump(exclude_unset=True)
        logger.debug(
            f"Updating user profile: user_id={current_user.id}, fields={list(updated_data.keys())}"
        )
        try:
            current_user = await self.repository.session.merge(current_user)
            result = await self.repository.update_profile(obj=current_user, data=updated_data)
            logger.success(
                f"User profile updated successfully: user_id={current_user.id}"
            )
            return UserResponse.model_validate(result)
        except Exception as e:
            logger.exception(
                f"Failed to update user profile: user_id={current_user.id}, error={str(e)}"
            )
            raise BaseAppException(
                message=f'Ошибка при попытке обновить профиль',
                log_message=f'Failed to update user profile: {current_user.id}: {str(e)}'

            )

    async def create_admin(self, payload: AdminCreate ) -> UserResponse:
        expected_key = config.ADMIN_SECRET_KEY

        if payload.admin_secret_key != expected_key:
            logger.warning(
                f"Admin creation denied: invalid admin_secret_key for email='{payload.email}'"
            )
            raise ForbiddenException(
                message=f'Неверный ключ',
                log_message=f'Failed to create admin user for email: {payload.email}'
            )

        existing_user = await self.repository.get_by_email(payload.email)
        if existing_user:
            raise ConflictException(
                f'Пользователь с {payload.email} уже существует'
            )

        hashed_password = hash_password(payload.password)

        new_admin_data = payload.model_dump(exclude={"admin_secret_key", "password"})
        new_admin_data['hashed_password'] = hashed_password
        new_admin_data['role'] = UserRoleEnum.ADMIN

        new_data = await self.repository.create(new_admin_data)
        logger.success(
            f"Admin user created: email='{new_data.email}', user_id={new_data.id}"
        )
        return UserResponse.model_validate(new_data)

    async def change_user_role(self, user_id: int, current_user: UserORM, payload: UserRoleUpdate) -> UserResponse:

        if current_user.role != UserRoleEnum.ADMIN:
            logger.warning(
                f"Role change denied: user_id={current_user.id} (role={current_user.role}) "
                f"attempted to change role for target_user_id={user_id}"
            )
            raise ForbiddenException(
                message=f'Только пользователи с ролью админ могут изменять роль',
                log_message=f'Access denied for user {user_id}',
            )

        updated_user = await self.repository.update(object_id=user_id, data=payload.model_dump())

        if not updated_user:
            raise NotFoundException(
                message=f'Пользователь не найден',
                log_message=f"Admin tried to update non-existent user {user_id}"
            )

        logger.success(
            f"User role updated: admin_user_id={current_user.id}, target_user_id={user_id}, new_role={payload.role}"
        )

        return UserResponse.model_validate(updated_user)
