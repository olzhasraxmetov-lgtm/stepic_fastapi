from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Boolean, DateTime, func, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.core.database import Base


class LessonORM(Base):
    __tablename__ = 'lessons'
    __table_args__ = (
        UniqueConstraint('course_id', 'order_number', name='uq_course_lesson_order'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[Text] = mapped_column(Text, nullable=False)

    order_number: Mapped[int] = mapped_column(Integer,nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'), index=True, nullable=False)

    course: Mapped['CourseORM'] = relationship(
        'CourseORM',
        back_populates='lessons',
    )