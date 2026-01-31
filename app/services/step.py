from typing import Sequence

from app.repositories.step import StepRepository
from app.schemas.step import StepCreate, StepUpdate, StepResponse
from app.models.lesson import LessonORM
from app.models.user import UserORM
from app.models.step import StepORM
from app.helpers.user_role import UserRoleEnum
from app.core.exceptions import ForbiddenException
from loguru import logger
class StepService:
    def __init__(self, step_repo: StepRepository):
        self.step_repo = step_repo

    async def _check_access(self, user: UserORM, lesson: LessonORM):
        if lesson.course.author_id != user.id and user.role != UserRoleEnum.ADMIN:
            raise ForbiddenException(message="Доступ запрещен")


    async def create_step(self, lesson: LessonORM, user: UserORM, payload: StepCreate) -> StepResponse:
        await self._check_access(user, lesson)

        data = payload.model_dump()

        if not data.get('order_number'):
            current_steps_count = await self.step_repo.get_count_by_lesson(lesson.id)
            data['order_number'] = current_steps_count + 1

        data['lesson_id'] = lesson.id
        new_data = await self.step_repo.create(data)
        logger.success(f"Step successfully created")
        return StepResponse.model_validate(new_data)

    async def update_step(self, step: StepORM, lesson: LessonORM, user: UserORM, payload: StepUpdate):
        await self._check_access(user, lesson)

        data = payload.model_dump(exclude_unset=True)
        updated_data = await self.step_repo.update(object_id=step.id, data=data)
        await self.step_repo.session.refresh(updated_data)
        logger.success(f"Step {step.id} update for lesson {lesson.id}")
        return StepResponse.model_validate(updated_data)

    async def delete_step(self, step: StepORM, lesson: LessonORM, user: UserORM) -> dict:
        await self._check_access(user, lesson)
        await self.step_repo.delete(object_id=step.id)
        logger.success(f"Step {step.id} deleted from lesson {lesson.id}")
        return {"message": "success"}

    async def get_all_steps(self, lesson: LessonORM, user: UserORM) -> Sequence[StepResponse]:
        await self._check_access(user, lesson)

        return await self.step_repo.get_all_steps(lesson.id)