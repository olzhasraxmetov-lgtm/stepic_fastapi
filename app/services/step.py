from typing import Sequence

from app.repositories.step import StepRepository
from app.schemas.step import StepCreate
from app.schemas.step import StepResponse
from app.models.lesson import LessonORM
from app.models.user import UserORM
from app.helpers.user_role import UserRoleEnum
from app.core.exceptions import ForbiddenException

class StepService:
    def __init__(self, step_repo: StepRepository):
        self.step_repo = step_repo

    async def create_step(self, lesson: LessonORM, user: UserORM, payload: StepCreate) -> StepResponse:
        if lesson.course.author_id != user.id and user.role != UserRoleEnum.ADMIN:
            raise ForbiddenException(message="Вы не являетесь автором этого курса")

        data = payload.model_dump()
        data['lesson_id'] = lesson.id
        new_data = await self.step_repo.create(data)
        return StepResponse.model_validate(new_data)

    async def get_all_steps(self, lesson_id: int) -> Sequence[StepResponse]:
        return await self.step_repo.get_all_steps(lesson_id)