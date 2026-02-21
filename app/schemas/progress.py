from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProgressResponseMe(BaseModel):
    course_id: int
    current_lesson_id: int | None = None
    completed_lessons: list[int] = []
    last_accessed: datetime
    is_completed: bool = False
    progress_percentage: float

    model_config = ConfigDict(from_attributes=True)