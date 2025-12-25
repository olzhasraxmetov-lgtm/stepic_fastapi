from typing import Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: ModelType):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> ModelType | None:
        result = await self.session.scalar(select(self.model).filter(self.model.id == id)) # type: ignore
        return result

    async def create(self, data: ModelType) -> ModelType:
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data