from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from app.schemas.step import StepResponse


class LessonBase(BaseModel):
    title: str = Field(..., description='Название урока', min_length=5, max_length=80)
    order_number: int = Field(..., ge=1, description='Порядковый номер урока')
    duration_minutes: int | None = Field(None, ge=1, description='Продолжительность урока в минутах')
    is_free: bool = Field(default=False, description='Бесплатный ли урок')

class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=80)
    order_number: int | None = Field(default=None, ge=1)
    duration_minutes: int | None = Field(default=None, ge=1)
    is_free: bool | None = None

class LessonResponse(LessonBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    steps: list[StepResponse] = []

    model_config = ConfigDict(from_attributes=True)