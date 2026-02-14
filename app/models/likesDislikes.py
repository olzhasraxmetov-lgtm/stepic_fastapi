from app.core.database import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime, func, Boolean

class LikesDislikesORM(Base):
    __tablename__ = 'likesDislikes'

    comment_id: Mapped[int] = mapped_column(
        ForeignKey('comments.id', ondelete='CASCADE'),
        primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    is_like: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )