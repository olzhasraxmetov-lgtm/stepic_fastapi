from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.core.dependencies import get_current_user
from app.core.dependencies import get_user_service
from app.models.user import UserORM
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService

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

@user_router.post('/login')
async def login(
        form: OAuth2PasswordRequestForm = Depends(),
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.login(form.username, form.password)

@user_router.get('/profile')
async def get_profile(
        user: UserORM = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
):
    pass