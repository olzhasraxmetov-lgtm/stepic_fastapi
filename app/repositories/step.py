from app.repositories.base import BaseRepository
from app.models.step import StepORM
from sqlalchemy import select, func, update


class StepRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, StepORM)

    async def get_all_steps(self, lesson_id: int):
        result = await self.session.scalars(
            select(StepORM).where(StepORM.lesson_id == lesson_id)
            .order_by(StepORM.order_number)
        )
        return result.all()

    async def get_count_by_lesson(self, lesson_id: int) -> int:
        query = select(func.count()).select_from(StepORM).where(StepORM.lesson_id == lesson_id)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def reorder_steps_after_delete(self, lesson_id: int, deleted_order_id: int):
        query = (
            update(StepORM)
            .where(StepORM.lesson_id == lesson_id)
            .where(StepORM.order_number > deleted_order_id)
            .values(order_number=StepORM.order_number - 1)
        )
        await self.session.execute(query)
        await self.session.commit()