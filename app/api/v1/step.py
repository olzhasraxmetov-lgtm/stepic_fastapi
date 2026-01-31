from typing import Annotated

from fastapi import APIRouter, Depends, Request, Query

from app.core.dependencies import get_current_user
from app.core.dependencies import get_step_service
from app.models.step import StepORM
from app.core.dependencies import valid_lesson
from app.schemas.step import StepCreate
from app.models.user import UserORM
from app.schemas.step import StepResponse
from app.services.step import StepService
from app.models.lesson import LessonORM

step_router = APIRouter(
    prefix="/{lesson_id}/steps",
    dependencies=[Depends(valid_lesson)],
)

@step_router.get('', tags=["Steps"])
async def get_steps(
    lesson_id: int,
    user: UserORM = Depends(get_current_user),
    step_service: StepService = Depends(get_step_service)
):
    return await step_service.get_all_steps(lesson_id)

@step_router.post('', tags=["Steps"], response_model=StepResponse)
async def create_step(
        payload: StepCreate,
        lesson: Annotated[LessonORM, Depends(valid_lesson)],
        lesson_id: int,
        user: UserORM = Depends(get_current_user),
        step_service: StepService = Depends(get_step_service)):
    return await step_service.create_step(user=user,  lesson=lesson, payload=payload)