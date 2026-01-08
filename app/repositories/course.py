from typing import Sequence

from sqlalchemy import select,delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query
from app.models.course import CourseORM
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CourseORM)

    async def get_my_courses(self, user_id: int) -> Sequence[CourseORM]:
        result = await self.session.scalars(
            select(CourseORM).where(CourseORM.author_id == user_id)
        )
        return result.all()

    async def delete_course(self, course_id: int) -> None:
        query = delete(CourseORM).where(CourseORM.id == course_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_paginated_courses_with_filters(
            self,
            page: int,
            per_page: int,
            min_price: float | None = None,
            max_price: float | None = None,
    ) -> dict:

        filters = [CourseORM.is_published == True]

        if min_price is not None:
            filters.append(CourseORM.price >= min_price)

        if max_price is not None:
            filters.append(CourseORM.price <= max_price)

        total_stmt = select(func.count()).select_from(CourseORM).where(*filters)

        total_count = await self.session.scalar(total_stmt) or 0

        data_query = await self.session.scalars(
            select(CourseORM)
            .where(*filters)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(CourseORM.id)
        )

        return {
            "items": data_query.all(),
            "page": page,
            "per_page": per_page,
            "total": total_count
        }