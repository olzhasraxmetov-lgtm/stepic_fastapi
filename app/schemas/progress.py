from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.course import CourseShortInfo


class ProgressResponseMe(BaseModel):
    course_id: int
    current_lesson_id: int | None = None
    completed_lessons: list[int] = []
    last_accessed: datetime
    is_completed: bool = False
    progress_percentage: float

    model_config = ConfigDict(from_attributes=True)

class UserCourseProgressList(BaseModel):
    progress_percentage: float
    last_accessed: datetime
    is_completed: bool
    current_lesson_id: int
    course: CourseShortInfo

    model_config = ConfigDict(from_attributes=True)