from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Numeric, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.core.database import Base


class CourseORM(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(130), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    price: Mapped[Decimal] = mapped_column(Numeric(10,2), default=0.0)

    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    author_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    author: Mapped['UserORM'] = relationship(
        'UserORM',
        back_populates='courses',
    )

    lessons: Mapped[list['LessonORM']] = relationship(
        'LessonORM',
        back_populates='course',
        cascade='all, delete-orphan',
    )
    
    purchases: Mapped[list['PurchaseORM']] = relationship(
        'PurchaseORM',
        back_populates='course',
    )

    comments: Mapped[list['CommentORM']] = relationship(
        'CommentORM',
        back_populates='course',
        cascade='all, delete-orphan',
    )