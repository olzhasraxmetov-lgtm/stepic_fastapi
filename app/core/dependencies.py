from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.core.database import AsyncSessionLocal
from collections.abc import AsyncGenerator
from fastapi.security import OAuth2PasswordBearer
from app.services.user import UserService
from app.repositories.user import UserRepository
from fastapi import Depends, HTTPException, status
from app.models.user import UserORM
from app.core.config import config
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session=db)


async def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository=repository)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_service: UserService = Depends(get_user_service)  # Используем уже готовый сервис
) -> UserORM:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("username")
        if not username:
            raise credentials_exception
    except (jwt.PyJWTError, jwt.ExpiredSignatureError):
        raise credentials_exception

    # Делегируем поиск пользователя сервису
    user = await user_service.repository.get_by_username(username)
    if not user:
        raise credentials_exception
    return user




