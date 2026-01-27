from datetime import datetime

from sqlalchemy import Integer, String, DateTime, func, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.core.database import Base
from app.helpers.user_role import UserRoleEnum


class UserORM(Base):
    __tablename__ = "users"


    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum),
        default=UserRoleEnum.USER,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    courses: Mapped[list['CourseORM']] = relationship(
        'CourseORM',
        back_populates='author',
        cascade='all, delete-orphan',
    )

    purchases: Mapped[list['PurchaseORM']] = relationship(
        'PurchaseORM',
        back_populates='user',
    )

    @property
    def can_create_courses(self) -> bool:
        return self.role in [UserRoleEnum.AUTHOR, UserRoleEnum.ADMIN]

    @property
    def is_admin(self) -> bool:
        return self.role == UserRoleEnum.ADMIN

    @property
    def is_author(self) -> bool:
        return self.role == UserRoleEnum.AUTHOR