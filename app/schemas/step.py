from pydantic import BaseModel, Field, ConfigDict
from app.helpers.step_type import StepType


class StepBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    step_type: StepType = Field(..., description='Тип урока')
    order_number: int | None = Field(None, ge=1, description='Порядковый номер урока')
    content: str | None = None
    video_url: str | None = None
    quiz_data: dict | None = None

class StepCreate(StepBase):
    pass

class StepUpdate(BaseModel):
    title: str | None = None
    step_type: StepType | None = None
    order_number: int | None = None
    content: str | None = None
    video_url: str | None = None
    quiz_data: dict | None = None

class StepResponse(StepBase):
    id: int
    lesson_id: int

    model_config = ConfigDict(from_attributes=True)