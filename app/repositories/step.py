from app.repositories.base import BaseRepository
from app.models.step import StepORM
from sqlalchemy import select


class StepRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, StepORM)

    async def get_all_steps(self, lesson_id: int):
        result = await self.session.scalars(
            select(StepORM).where(StepORM.lesson_id == lesson_id)
            .order_by(StepORM.order_number)
        )
        return result.all()