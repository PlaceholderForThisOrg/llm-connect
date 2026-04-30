from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models import AtomicPointRelation


class AtomicPointRelationRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create(self, relations: List[AtomicPointRelation]):
        self.session.add_all(relations)
        await self.session.flush()

    async def create(self, relation: AtomicPointRelation):
        self.session.add(relation)
        await self.session.flush()
        return relation

    async def find_relation(self, from_id, to_id, relation_type):
        stmt = select(AtomicPointRelation).where(
            AtomicPointRelation.from_id == from_id,
            AtomicPointRelation.to_id == to_id,
            AtomicPointRelation.relation_type == relation_type,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
