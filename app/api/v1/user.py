from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService
from app.core.dependencies import get_user_service

user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@user_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(
        user: UserCreate,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.register(user)