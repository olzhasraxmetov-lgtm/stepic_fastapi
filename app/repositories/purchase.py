from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.purchace import PurchaseORM

class PurchaseRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session,PurchaseORM)