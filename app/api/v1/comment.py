from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.services.comment import CommentService

comment_router = APIRouter(tags=["Comments"])

@comment_router.get("/steps/{step_id}/comments")
async def get_step_comments():
    pass

@comment_router.post("/steps/{step_id}/comments")
async def post_step_comments():
    pass

@comment_router.post("/comments/{comment_id}/replies")
async def reply_to_comment():
    pass

@comment_router.delete("/comments/{comment_id}")
async def delete_comment():
    pass

@comment_router.patch("/comments/{comment_id}")
async def update_comment():
    pass

@comment_router.get("/courses/{course_id}/comments")
async def get_course_wide_comments():
    pass