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
    reaction_service: ReactionService = Depends(get_reaction_service),
):
    return await reaction_service.toggle_reaction(comment_id, user, is_like=True)

@reactions_router.post('/comments/{comment_id}/dislike')
async def toggle_comment_dislike(
    comment_id: int,
    user: UserORM = Depends(get_current_user),
    reaction_service: ReactionService = Depends(get_reaction_service),
):
    return await reaction_service.toggle_reaction(comment_id, user, is_like=False)
