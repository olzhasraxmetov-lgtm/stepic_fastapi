from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status
from app.schemas.comment import CommentCreate, CommentUpdate
from app.core.dependencies import get_current_user, validation_course_id
from app.core.dependencies import get_comment_service
from app.services.comment import CommentService
from app.models.user import UserORM
from app.schemas.comment import CommentFullResponse, CommentShortResponse
from app.models.course import CourseORM

comment_router = APIRouter(tags=["Comments"])

@comment_router.get("/steps/{step_id}/comments", response_model=list[CommentFullResponse])
async def get_step_comments(
        step_id: int,
        user: UserORM = Depends(get_current_user),
        comment_service: CommentService = Depends(get_comment_service),

):
    return await comment_service.get_tree_of_comments(step_id, user)

@comment_router.post("/steps/{step_id}/comments")
async def post_step_comments(
        step_id: int,
        payload: CommentCreate,
        user: UserORM = Depends(get_current_user),
        comment_service: CommentService = Depends(get_comment_service)
):
    return await comment_service.leave_comment(step_id=step_id, user=user, content=payload.content)

@comment_router.post("/comments/{comment_id}/replies")
async def reply_to_comment(
        comment_id: int,
        payload: CommentCreate,
        user: UserORM = Depends(get_current_user),
        comment_service: CommentService = Depends(get_comment_service)
):
    return await comment_service.reply_to_comment(comment_id=comment_id, user=user, content=payload.content)

@comment_router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentShortResponse)
async def delete_comment(
        comment_id: int,
        user: UserORM = Depends(get_current_user),
        comment_service: CommentService = Depends(get_comment_service)
):
    return await comment_service.soft_delete_comment(comment_id=comment_id, user=user)

@comment_router.patch("/comments/{comment_id}")
async def update_comment(
        comment_id: int,
        payload: CommentUpdate,
        user: UserORM = Depends(get_current_user),
        comment_service: CommentService = Depends(get_comment_service),
):
    return await comment_service.update_comment(comment_id, user, payload)

@comment_router.get("/courses/{course_id}/comments", response_model=list[CommentShortResponse])
async def get_course_wide_comments(
        course_id: int,
        course: CourseORM = Depends(validation_course_id),
        user: UserORM = Depends(get_current_user),
        comment_service: CommentService = Depends(get_comment_service)
):
    return await comment_service.get_all_course_comments(course_id, user)