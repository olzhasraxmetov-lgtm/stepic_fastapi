from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from pydantic import Field


class CourseBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=130, description='Название курса')
    description: str | None = Field(default=None, min_length=20, description='Описание курса')
    price: Decimal = Field(default=Decimal("0.0"), max_digits=10, decimal_places=2, description='Цена курса')

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=20, max_length=130)
    description: str | None = Field(default=None, min_length=20)
    price: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)

class CourseResponse(CourseBase):
    id: int
    author_id: int

    is_published: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CourseList(BaseModel):
    items: list[CourseResponse]
    page: int
    per_page: int
    total: int