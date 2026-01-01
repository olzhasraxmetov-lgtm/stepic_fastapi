from typing import Generic, TypeVar, Type

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> ModelType | None:
        result = await self.session.scalar(select(self.model).filter(self.model.id == id)) # type: ignore
        return result

    async def create(self, data: ModelType) -> ModelType:
        db_obj = self.model(**data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, object_id: int, data: dict) -> ModelType | None:
        query = (
            update(self.model)
            .where(self.model.id == object_id)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().first()