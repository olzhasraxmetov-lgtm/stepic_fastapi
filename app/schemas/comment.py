from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=3000, description='Содержимое комментария')

class CommentCreate(CommentBase):
    pass

class CommentReplyCreate(CommentCreate):
    parent_id: int

class CommentUpdate(BaseModel):
    content: str | None = None

class CommentAuthor(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

class CommentResponse(CommentBase):
    id: int

    parent_id: int | None = None
    step_title: str | None = None
    created_at: datetime
    updated_at: datetime
    author: CommentAuthor
    is_edited: bool = False
    is_deleted: bool = False
    children: list["CommentResponse"] = []

    model_config = ConfigDict(from_attributes=True)



CommentResponse.model_rebuild()