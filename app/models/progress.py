from datetime import datetime
from decimal import Decimal

from app.core.database import Base
from sqlalchemy import Boolean, ForeignKey, Numeric, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class UserCourseProgressORM(Base):
    __tablename__ = "user_course_progress"

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="_user_course_progress_uc"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id', ondelete="CASCADE"),nullable=False)
    current_lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id', ondelete="SET NULL"), nullable=True)
    progress_percentage: Mapped[Decimal] = mapped_column(Numeric(10,2))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    last_accessed: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class UserLessonCompletionORM(Base):
    __tablename__ = "user_lesson_completions"

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="_user_lesson_completion_uc"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id',ondelete="CASCADE"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id',ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id',ondelete="CASCADE"), nullable=False)

    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())