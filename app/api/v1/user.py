from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.core.dependencies import get_current_user
from app.core.dependencies import get_user_service
from app.models.user import UserORM
from app.schemas.user import AdminCreate
from app.schemas.user import UserCreate, UserResponse, UserPublic, UserUpdate
from app.schemas.user import UserRoleUpdate
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

@user_router.get('/my_profile', response_model=UserResponse)
async def get_profile(
        user: UserORM = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_profile(user)

@user_router.get('/{user_id}/profile', response_model=UserPublic)
async def get_public_profile(
        user_id: int,
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_public_profile_by_id(user_id)

@user_router.put('/my_profile', response_model=UserResponse)
async def update_profile(
        user_update: UserUpdate,
        user: UserORM = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_profile(current_user=user, payload=user_update)

@user_router.post('/register/admin', response_model=UserResponse)
async def register_admin(
        payload: AdminCreate,
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.create_admin(payload=payload)

@user_router.patch('/admin/{user_id}/role', response_model=UserResponse)
async def update_user_role(
        user_id: int,
        payload: UserRoleUpdate,
        current_user: UserORM = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.change_user_role(user_id=user_id, current_user=current_user, payload=payload)