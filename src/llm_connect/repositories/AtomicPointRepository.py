# from llm_connect.proto.atomic_points import ATOMIC_REGISTRY


from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from llm_connect.models.AtomicPoint import AtomicPoint
from llm_connect.models.AtomicPointTag import AtomicPointTag
from llm_connect.models.Tag import Tag
from llm_connect.proto.atomic_points_v2 import ATOMIC_REGISTRY


class AtomicPointRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_id(self, id: str):
        stmt = select(AtomicPoint).where(AtomicPoint.id == id)

        result = await self.session.execute(stmt)

        return result.scalar()

    def get_atomic_point_by_id(self, ap_id: str):
        return ATOMIC_REGISTRY[ap_id]

    async def create(self, atomic_point: AtomicPoint):
        self.session.add(atomic_point)
        await self.session.flush()
        return atomic_point

    async def search(
        self,
        search: Optional[str],
        type: Optional[str],
        level: Optional[str],
        tags: Optional[List[str]],
        min_popularity: Optional[float],
        page: int,
        page_size: int,
    ) -> Tuple[List[AtomicPoint], int]:

        query = select(AtomicPoint).options(
            selectinload(AtomicPoint.atomic_point_tags).selectinload(AtomicPointTag.tag)
        )

        count_query = select(func.count(AtomicPoint.id))

        if search:
            condition = AtomicPoint.name.ilike(
                f"%{search}%"
            ) | AtomicPoint.description.ilike(f"%{search}%")
            query = query.where(condition)
            count_query = count_query.where(condition)

        if type:
            query = query.where(AtomicPoint.type == type)
            count_query = count_query.where(AtomicPoint.type == type)

        if level:
            query = query.where(AtomicPoint.level == level)
            count_query = count_query.where(AtomicPoint.level == level)

        if min_popularity:
            query = query.where(AtomicPoint.popularity >= min_popularity)
            count_query = count_query.where(AtomicPoint.popularity >= min_popularity)

        if tags:
            query = (
                query.join(AtomicPoint.atomic_point_tags)
                .join(AtomicPointTag.tag)
                .where(Tag.name.in_(tags))
                .distinct()
            )

            count_query = (
                count_query.join(AtomicPoint.atomic_point_tags)
                .join(AtomicPointTag.tag)
                .where(Tag.name.in_(tags))
                .distinct()
            )

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        items = result.scalars().all()

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        return items, total
