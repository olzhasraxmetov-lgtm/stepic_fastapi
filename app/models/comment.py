from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.core.database import Base

class CommentORM(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True)

    step_id: Mapped[int] = mapped_column(ForeignKey('steps.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id', ondelete='CASCADE'))
    content: Mapped[Text] = mapped_column(Text, nullable=False)

    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id", ondelete='CASCADE'), nullable=True)

    parent: Mapped["CommentORM | None "] = relationship("CommentORM", back_populates="children", remote_side=[id])

    children: Mapped[list['CommentORM']] = relationship("CommentORM", back_populates="parent")

    course: Mapped['CourseORM'] = relationship("CourseORM", back_populates="comments")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )