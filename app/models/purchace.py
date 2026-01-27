from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func, Numeric, UniqueConstraint, String
from datetime import datetime
from decimal import Decimal
from app.helpers.purchase_status import PurchaseStatus


class PurchaseORM(Base):
    __tablename__ = "purchases"

    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_purchase_user_course'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[PurchaseStatus] = mapped_column(default=PurchaseStatus.PENDING)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)

    purchase_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    price_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    user: Mapped['UserORM'] = relationship("UserORM", back_populates="purchases")
    course: Mapped['PurchaseORM'] = relationship("PurchaseORM", back_populates="purchases")