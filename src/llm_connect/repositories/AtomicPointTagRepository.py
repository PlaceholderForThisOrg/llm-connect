from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models.AtomicPointTag import AtomicPointTag


class AtomicPointTagRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def bulk_create(self, relations: list[AtomicPointTag]):
        self.db.add_all(relations)
