from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from llm_connect.models.Tag import Tag


class TagRepository:
    def __init__(self, ses: AsyncSession):
        self.ses = ses

    async def create_tag(self, name: str) -> Tag:
        tag = Tag(id=str(uuid.uuid4()),name=name,)

        # stage the object
        self.ses.add(tag)
        # push to DB to get PK (if needed)
        await self.ses.flush()

        return tag
    
    async def get_all(self, limit: int = 10, offset: int = 0):
        stmt = (
            select(Tag)
            .order_by(Tag.name)
            .limit(limit)
            .offset(offset)
        )

        result = await self.ses.execute(stmt)
        return result.scalars().all()
    
    async def count_all(self) -> int:
        stmt = select(func.count(Tag.id))
        result = await self.ses.execute(stmt)
        return result.scalar_one()