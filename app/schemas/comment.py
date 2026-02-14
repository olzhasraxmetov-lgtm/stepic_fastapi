from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal

class CommentAuthor(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=3000, description='Содержимое комментария')
    id: int
    created_at: datetime
    author: CommentAuthor
    is_deleted: bool = False
    model_config = ConfigDict(from_attributes=True)

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=3000, description='Содержимое комментария')

class CommentUpdate(BaseModel):
    content: str | None = None

class CommentShortResponse(CommentBase):
    step_title: str | None = None
    parent_id: int | None = None
    is_edited: bool = False
    likes_count: int = 0
    dislikes_count: int = 0

class CommentFullResponse(CommentBase):
    parent_id: int | None = None
    step_title: str | None = None
    is_edited: bool = False
    updated_at: datetime

    likes_count: int = 0
    dislikes_count: int = 0
    is_liked_by_me: bool = False
    is_disliked_by_me: bool = False
    children: list["CommentFullResponse"] = []

CommentFullResponse.model_rebuild()