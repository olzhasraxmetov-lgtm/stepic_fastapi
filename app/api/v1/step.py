from typing import Annotated

from fastapi import APIRouter, Depends, Request, Query

from app.core.dependencies import get_current_user
from app.core.dependencies import get_step_service
from app.core.dependencies import valid_step
from app.models.step import StepORM
from app.core.dependencies import valid_lesson
from app.schemas.step import StepCreate
from app.models.user import UserORM
from app.schemas.step import StepResponse, StepUpdate
from app.services.step import StepService
from app.models.lesson import LessonORM

step_router = APIRouter(
    prefix="/{lesson_id}/steps",
)

@step_router.get('', tags=["Steps"], response_model=list[StepResponse])
async def get_steps(
    lesson: Annotated[LessonORM, Depends(valid_lesson)],
    user: Annotated[UserORM, Depends(get_current_user)],
    step_service: Annotated[StepService, Depends(get_step_service)]
):
    return await step_service.get_all_steps(lesson, user)

@step_router.post('', tags=["Steps"], response_model=StepResponse)
async def create_step(
        payload: StepCreate,
        lesson: Annotated[LessonORM, Depends(valid_lesson)],
        user: Annotated[UserORM, Depends(get_current_user)],
        step_service: Annotated[StepService, Depends(get_step_service)]
):
    return await step_service.create_step(user=user, lesson=lesson, payload=payload)

@step_router.patch('/{step_id}', tags=["Steps"], response_model=StepResponse)
async def update_step(
        payload: StepUpdate,
        step: Annotated[StepORM, Depends(valid_step)],
        lesson: Annotated[LessonORM, Depends(valid_lesson)],
        user: Annotated[UserORM, Depends(get_current_user)],
        step_service: Annotated[StepService, Depends(get_step_service)]
):
    return await step_service.update_step(step=step,user=user, lesson=lesson, payload=payload)

@step_router.delete('/{step_id}', tags=["Steps"])
async def delete_step(
        step: Annotated[StepORM, Depends(valid_step)],
        lesson: Annotated[LessonORM, Depends(valid_lesson)],
        user: Annotated[UserORM, Depends(get_current_user)],
        step_service: Annotated[StepService, Depends(get_step_service)]
):
    return await step_service.delete_step(step=step,user=user, lesson=lesson)