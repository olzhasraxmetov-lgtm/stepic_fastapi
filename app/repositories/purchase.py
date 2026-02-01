from decimal import Decimal
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert
from app.helpers.purchase_status import PurchaseStatus
from app.models.course import CourseORM
from app.models.purchace import PurchaseORM
from app.repositories.base import BaseRepository


class PurchaseRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session,PurchaseORM)

    async def get_purchase_by_user_and_course(self, user_id: int, course_id: int) -> PurchaseORM | None:
        query = select(PurchaseORM).where(
            PurchaseORM.user_id == user_id,
            PurchaseORM.course_id == course_id,
            PurchaseORM.status == PurchaseStatus.SUCCEEDED
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add(self, purchase: PurchaseORM) -> PurchaseORM | None:
        self.session.add(purchase)

    async def upsert_purchase(self, data: dict) -> PurchaseORM:
        stmt = insert(PurchaseORM).values(**data)

        stmt = stmt.on_conflict_do_update(
            constraint="uq_purchase_user_course",
            set_={
                "status": data["status"],
                "price_paid": data["price_paid"],
                "payment_id": data["payment_id"]
            }
        ).returning(PurchaseORM)

        result = await self.session.execute(stmt)
        return result.scalar_one()


    async def get_payment_by_id(self, payment_id: str) -> PurchaseORM | None:
        result = await self.session.scalar(select(PurchaseORM).filter(PurchaseORM.payment_id==payment_id))
        return result

    async def get_by_id_with_courses(self, purchase_id: int) -> PurchaseORM | None:
        query = select(PurchaseORM).options(
            selectinload(PurchaseORM.course)

        ).where(PurchaseORM.id == purchase_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_status(self, purchase: PurchaseORM, new_status: PurchaseStatus) -> None:
        purchase.status = new_status

    async def get_purchased_courses(self, user_id: int) -> Sequence[CourseORM]:
        query = select(CourseORM).join(PurchaseORM, CourseORM.id==PurchaseORM.course_id).where(
            PurchaseORM.user_id == user_id,
            PurchaseORM.status == PurchaseStatus.SUCCEEDED
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def check_purchased_confirmed(self, user_id: int, course_id: int):
        query = (
            select(PurchaseORM)
            .where(PurchaseORM.user_id == user_id)
            .where(PurchaseORM.course_id == course_id)
            .where(PurchaseORM.status == PurchaseStatus.SUCCEEDED)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None