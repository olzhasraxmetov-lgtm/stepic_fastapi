from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal


class LessonBase(BaseModel):
    title: str = Field(..., description='Название урока', min_length=5, max_length=80)
    content: str = Field(...,min_length=1, description='Содержимое урока')
    order_number: int = Field(..., ge=1, description='Порядковый номер урока')
    duration_minutes: int | None = Field(None, ge=1, description='Продолжительность урока в минутах')


class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=80)
    content: str | None = Field(default=None, min_length=1)
    order_number: int | None = Field(default=None, ge=1)
    duration_minutes: int | None = Field(default=None, ge=1)

class LessonResponse(LessonBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)