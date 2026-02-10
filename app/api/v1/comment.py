from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status
from app.schemas.comment import CommentCreate, CommentReplyCreate
from app.core.dependencies import get_current_user
from app.core.dependencies import get_comment_service
from app.services.comment import CommentService
from app.models.user import UserORM
from app.schemas.comment import CommentResponse


comment_router = APIRouter(tags=["Comments"])

@comment_router.get("/steps/{step_id}/comments", response_model=list[CommentResponse])
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

@comment_router.delete("/comments/{comment_id}")
async def delete_comment():
    pass

@comment_router.patch("/comments/{comment_id}")
async def update_comment():
    pass

@comment_router.get("/courses/{course_id}/comments")
async def get_course_wide_comments():
    pass