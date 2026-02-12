from sqlalchemy import String, Text, ForeignKey, Integer, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.core.database import Base
from app.helpers.step_type import StepType

class StepORM(Base):
    __tablename__ = 'steps'
    __table_args__ = (
        UniqueConstraint('lesson_id', 'order_number', name='uq_lesson_step_order'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    step_type: Mapped[StepType] = mapped_column(String(20), default=StepType.TEXT)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    video_url: Mapped[str] = mapped_column(String, nullable=True)
    order_number: Mapped[int] = mapped_column(Integer, default=1)
    quiz_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    lesson: Mapped['LessonORM'] = relationship(
        'LessonORM',
        back_populates='steps',
    )
    comments: Mapped[list["CommentORM"]] = relationship(
        "CommentORM",
        back_populates="step",
        cascade="all, delete-orphan"
    )