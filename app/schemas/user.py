from datetime import datetime

from pydantic import BaseModel
from pydantic import Field, EmailStr, ConfigDict

from app.helpers.user_role import UserRoleEnum


class UserBase(BaseModel):
    username: str = Field(min_length=5, max_length=15, description='Имя пользователя')
    email: EmailStr = Field(description='Email пользователя')
    full_name: str = Field(min_length=10, max_length=25,description='Полное имя пользователя')


class UserCreate(UserBase):
    password: str = Field(min_length=5, max_length=35)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=5, max_length=15)
    email: EmailStr | None = None
    full_name: str | None =Field(default=None, min_length=10, max_length=25)

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: UserRoleEnum = UserRoleEnum.USER
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    username: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)

class AdminCreate(UserCreate):
    admin_secret_key: str