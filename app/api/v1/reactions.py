from fastapi import APIRouter, Depends
from app.models.user import UserORM
from app.core.dependencies import get_current_user
from app.core.dependencies import get_reaction_service
from app.services.reaction import ReactionService

reactions_router = APIRouter(
    prefix="/reactions",
    tags=["Reactions"]
)


@reactions_router.post('/comments/{comment_id}/like')
async def toggle_comment_like(
    comment_id: int,
    user: UserORM = Depends(get_current_user),
    service: ReactionService = Depends(get_reaction_service),
):
    pass

@reactions_router.post('/comments/{comment_id}/dislike')
async def toggle_comment_dislike(comment_id: int):
    pass
